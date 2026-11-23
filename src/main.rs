use directories::ProjectDirs;
use eframe::egui;
use enigo::{Enigo, Key, Keyboard, Settings};
use rand::Rng;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc,
};
use std::thread;
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct AppConfig {
    wpm: u32,
    jitter_pct: u32,
    typo_chance_pct: u32,
    start_delay_sec: u32,
    enable_typos: bool,
    punctuation_pause_ms: u64,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            wpm: 65,
            jitter_pct: 30,
            typo_chance_pct: 4,
            start_delay_sec: 3,
            enable_typos: true,
            punctuation_pause_ms: 140,
        }
    }
}

fn config_file_path() -> Option<PathBuf> {
    ProjectDirs::from("com", "Lucaas-o", "HumanLikeTyper").map(|dirs| {
        let dir = dirs.config_dir().to_path_buf();
        dir.join("config.json")
    })
}

fn load_config() -> AppConfig {
    let Some(path) = config_file_path() else {
        return AppConfig::default();
    };
    fs::read_to_string(path)
        .ok()
        .and_then(|raw| serde_json::from_str::<AppConfig>(&raw).ok())
        .unwrap_or_default()
}

fn save_config(cfg: &AppConfig) -> Result<(), String> {
    let Some(path) = config_file_path() else {
        return Err("Could not determine OS configuration directory.".into());
    };
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("Failed to create config folder: {e}"))?;
    }
    let json = serde_json::to_string_pretty(cfg).map_err(|e| format!("Failed to serialize settings: {e}"))?;
    fs::write(path, json).map_err(|e| format!("Failed to write settings: {e}"))?;
    Ok(())
}

fn nearby_typo_char(expected: char) -> Option<char> {
    let lower = expected.to_ascii_lowercase();
    let neighbors: &[char] = match lower {
        'a' => &['s', 'q', 'w', 'z'],
        'e' => &['w', 'r', 'd', 's'],
        'i' => &['u', 'o', 'k', 'j'],
        'o' => &['i', 'p', 'l', 'k'],
        'u' => &['y', 'i', 'j', 'h'],
        's' => &['a', 'd', 'w', 'e', 'x', 'z'],
        'd' => &['s', 'f', 'e', 'r', 'c', 'x'],
        'f' => &['d', 'g', 'r', 't', 'v', 'c'],
        'n' => &['b', 'm', 'h', 'j'],
        't' => &['r', 'y', 'f', 'g'],
        _ => return None,
    };
    let mut rng = rand::thread_rng();
    let pick = neighbors[rng.gen_range(0..neighbors.len())];
    if expected.is_ascii_uppercase() {
        Some(pick.to_ascii_uppercase())
    } else {
        Some(pick)
    }
}

fn run_typing_worker(
    text: String,
    cfg: AppConfig,
    stop_flag: Arc<AtomicBool>,
    is_running: Arc<AtomicBool>,
    status_msg: Arc<std::sync::Mutex<String>>,
) {
    let set_status = |msg: &str| {
        if let Ok(mut guard) = status_msg.lock() {
            *guard = msg.to_string();
        }
    };

    if cfg.start_delay_sec > 0 {
        for remaining in (1..=cfg.start_delay_sec).rev() {
            if stop_flag.load(Ordering::Relaxed) {
                set_status("Cancelled before start.");
                is_running.store(false, Ordering::Relaxed);
                return;
            }
            set_status(&format!("Starting in {remaining}s... switch to target input."));
            thread::sleep(Duration::from_secs(1));
        }
    }

    let mut enigo = match Enigo::new(&Settings::default()) {
        Ok(e) => e,
        Err(err) => {
            set_status(&format!("Failed to initialize keyboard input: {err}"));
            is_running.store(false, Ordering::Relaxed);
            return;
        }
    };

    set_status("Typing...");

    // Standard word = 5 chars => chars_per_sec = (wpm * 5) / 60
    let wpm = cfg.wpm.max(10) as f64;
    let base_delay_ms = (60_000.0 / (wpm * 5.0)).clamp(12.0, 600.0);
    let jitter_ratio = (cfg.jitter_pct.min(90) as f64) / 100.0;

    let mut rng = rand::thread_rng();
    let chars: Vec<char> = text.chars().collect();
    let mut i = 0;

    while i < chars.len() {
        if stop_flag.load(Ordering::Relaxed) {
            set_status("Stopped by user.");
            is_running.store(false, Ordering::Relaxed);
            return;
        }

        let ch = chars[i];

        // Optional realistic typo + backspace correction
        let can_typo = cfg.enable_typos
            && ch.is_ascii_alphabetic()
            && rng.gen_range(0..100) < cfg.typo_chance_pct;

        if can_typo {
            if let Some(wrong_ch) = nearby_typo_char(ch) {
                let _ = enigo.text(&wrong_ch.to_string());
                let typo_pause = rng.gen_range(90..=220);
                thread::sleep(Duration::from_millis(typo_pause));
                if stop_flag.load(Ordering::Relaxed) {
                    set_status("Stopped by user.");
                    is_running.store(false, Ordering::Relaxed);
                    return;
                }
                let _ = enigo.key(Key::Backspace, enigo::Direction::Click);
                thread::sleep(Duration::from_millis(rng.gen_range(50..=130)));
            }
        }

        if ch == '\n' {
            let _ = enigo.key(Key::Return, enigo::Direction::Click);
        } else if ch == '\t' {
            let _ = enigo.key(Key::Tab, enigo::Direction::Click);
        } else {
            let _ = enigo.text(&ch.to_string());
        }

        let min_ms = (base_delay_ms * (1.0 - jitter_ratio)).max(8.0) as u64;
        let max_ms = (base_delay_ms * (1.0 + jitter_ratio)).max(min_ms + 1) as u64;
        let mut sleep_ms = rng.gen_range(min_ms..=max_ms);

        if matches!(ch, '.' | ',' | '!' | '?' | ';' | ':') {
            sleep_ms += rng.gen_range(50..=cfg.punctuation_pause_ms.max(60));
        }

        thread::sleep(Duration::from_millis(sleep_ms));
        i += 1;
    }

    set_status("Completed.");
    is_running.store(false, Ordering::Relaxed);
}

struct HumanTyperApp {
    input_text: String,
    config: AppConfig,
    stop_flag: Arc<AtomicBool>,
    is_running: Arc<AtomicBool>,
    status_msg: Arc<std::sync::Mutex<String>>,
    last_save_error: Option<String>,
}

impl HumanTyperApp {
    fn new(cc: &eframe::CreationContext<'_>) -> Self {
        cc.egui_ctx.set_visuals(egui::Visuals::dark());
        Self {
            input_text: String::from("Hello! This text is being typed at a natural human pace."),
            config: load_config(),
            stop_flag: Arc::new(AtomicBool::new(false)),
            is_running: Arc::new(AtomicBool::new(false)),
            status_msg: Arc::new(std::sync::Mutex::new(String::from("Ready."))),
            last_save_error: None,
        }
    }

    fn persist(&mut self) {
        if let Err(err) = save_config(&self.config) {
            self.last_save_error = Some(err);
        } else {
            self.last_save_error = None;
        }
    }
}

impl eframe::App for HumanTyperApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        let running = self.is_running.load(Ordering::Relaxed);
        if running {
            ctx.request_repaint_after(Duration::from_millis(100));
        }

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Human-Like Typer");
            ui.label("Simulate natural keyboard input with timing variation and optional corrections.");
            ui.add_space(8.0);

            ui.label("Text to type:");
            ui.add_enabled(
                !running,
                egui::TextEdit::multiline(&mut self.input_text)
                    .desired_rows(6)
                    .desired_width(f32::INFINITY)
                    .hint_text("Paste or write the text you want typed..."),
            );

            ui.add_space(10.0);
            ui.separator();
            ui.add_space(8.0);

            let mut changed = false;

            ui.horizontal(|ui| {
                ui.label("Speed (WPM):");
                if ui
                    .add_enabled(!running, egui::Slider::new(&mut self.config.wpm, 15..=180))
                    .changed()
                {
                    changed = true;
                }
            });

            ui.horizontal(|ui| {
                ui.label("Timing jitter (%):");
                if ui
                    .add_enabled(!running, egui::Slider::new(&mut self.config.jitter_pct, 0..=80))
                    .changed()
                {
                    changed = true;
                }
            });

            ui.horizontal(|ui| {
                ui.label("Start delay (sec):");
                if ui
                    .add_enabled(!running, egui::Slider::new(&mut self.config.start_delay_sec, 0..=15))
                    .changed()
                {
                    changed = true;
                }
            });

            if ui
                .add_enabled(
                    !running,
                    egui::Checkbox::new(&mut self.config.enable_typos, "Simulate occasional typos & backspace"),
                )
                .changed()
            {
                changed = true;
            }

            if self.config.enable_typos {
                ui.horizontal(|ui| {
                    ui.label("Typo chance (%):");
                    if ui
                        .add_enabled(!running, egui::Slider::new(&mut self.config.typo_chance_pct, 1..=20))
                        .changed()
                    {
                        changed = true;
                    }
                });
            }

            if changed {
                self.persist();
            }

            ui.add_space(12.0);

            ui.horizontal(|ui| {
                let can_start = !running && !self.input_text.is_empty();
                if ui.add_enabled(can_start, egui::Button::new("Start Typing")).clicked() {
                    self.stop_flag.store(false, Ordering::Relaxed);
                    self.is_running.store(true, Ordering::Relaxed);

                    let text_clone = self.input_text.clone();
                    let cfg_clone = self.config.clone();
                    let stop_clone = Arc::clone(&self.stop_flag);
                    let running_clone = Arc::clone(&self.is_running);
                    let status_clone = Arc::clone(&self.status_msg);

                    thread::spawn(move || {
                        run_typing_worker(text_clone, cfg_clone, stop_clone, running_clone, status_clone);
                    });
                }

                if ui.add_enabled(running, egui::Button::new("Stop")).clicked() {
                    self.stop_flag.store(true, Ordering::Relaxed);
                }

                if ui.add_enabled(!running, egui::Button::new("Reset Defaults")).clicked() {
                    self.config = AppConfig::default();
                    self.persist();
                }
            });

            ui.add_space(10.0);

            let current_status = self
                .status_msg
                .lock()
                .map(|s| s.clone())
                .unwrap_or_else(|_| "Ready.".to_string());
            ui.label(format!("Status: {current_status} ({} chars)", self.input_text.chars().count()));

            if let Some(err) = &self.last_save_error {
                ui.colored_label(egui::Color32::YELLOW, format!("Settings warning: {err}"));
            }
        });
    }
}

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([480.0, 420.0]),
        ..Default::default()
    };

    eframe::run_native(
        "Human-Like Typer",
        options,
        Box::new(|cc| Ok(Box::new(HumanTyperApp::new(cc)))),
    )
}