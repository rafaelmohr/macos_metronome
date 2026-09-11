import SwiftUI

/// Every tunable constant: sizing, limits, timing. Ported 1:1 from
/// metronome/config.py so behavior stays identical to the Python app.
enum Config {
    // --- window ---
    static let windowWidth: CGFloat = 560
    static let windowHeight: CGFloat = 420
    static let windowTitle = "Metronome"

    // --- musical limits ---
    static let startTempo = 120
    static let minTempo = 20
    static let maxTempo = 300

    static let startBeatsPerBar = 4
    static let minBeatsPerBar = 1
    static let maxBeatsPerBar = 32

    static let tempoStepSmall = 1
    static let tempoStepLarge = 5

    // --- held-key auto-repeat behaviour (arrow keys / N / M) ---
    static let keyRepeatInitialDelayMs: Double = 400
    static let keyRepeatIntervalMs: Double = 110
    static let keyRepeatFastAfterMs: Double = 1500
    static let keyRepeatFastIntervalMs: Double = 40

    // --- BPM keyboard text-entry ---
    static let bpmEntryMaxDigits = 3
    static let cursorBlinkIntervalSeconds: TimeInterval = 0.5
    static let bpmAutoConfirmDelaySeconds: TimeInterval = 1.0

    // --- beat indicator ---
    static let minLabelCellWidth: CGFloat = 18

    // --- fonts ---
    static let fontName = "Arial"
    static let fontSizeBpm: CGFloat = 116
    static let fontSizeSmall: CGFloat = 16
    static let fontSizeHint: CGFloat = 13
    static let fontSizeLegendTitle: CGFloat = 22
    static let fontSizeLegendBody: CGFloat = 16

    static func font(_ size: CGFloat, bold: Bool = false) -> Font {
        .custom(fontName, size: size).weight(bold ? .bold : .regular)
    }
}

/// Theme: dark, modern, flat. Ported 1:1 from metronome/config.py's Color class.
enum AppColor {
    static let background = Color(red: 16 / 255, green: 17 / 255, blue: 21 / 255)
    static let panel = Color(red: 26 / 255, green: 27 / 255, blue: 34 / 255)
    static let panelBorder = Color(red: 42 / 255, green: 44 / 255, blue: 54 / 255)
    static let textPrimary = Color(red: 237 / 255, green: 237 / 255, blue: 242 / 255)
    static let textSecondary = Color(red: 144 / 255, green: 146 / 255, blue: 163 / 255)
    static let textMuted = Color(red: 96 / 255, green: 98 / 255, blue: 114 / 255)

    static let accent = Color(red: 92 / 255, green: 170 / 255, blue: 255 / 255)
    static let downbeat = Color(red: 255 / 255, green: 122 / 255, blue: 89 / 255)

    static let beatActive = accent
    static let beatDownbeatActive = downbeat
    static let beatInactive = Color(red: 46 / 255, green: 48 / 255, blue: 58 / 255)

    static let pause = Color(red: 255 / 255, green: 196 / 255, blue: 80 / 255)
    static let editBorder = accent
    static let overlayScrim = Color.black.opacity(170.0 / 255.0)
}
