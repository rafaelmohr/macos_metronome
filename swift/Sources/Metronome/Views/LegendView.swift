import SwiftUI

/// A toggleable overlay listing every mouse and keyboard control.
///
/// Kept data-driven (a plain list of (control, description) pairs) so
/// adding a new shortcut later just means adding a row here. Port of
/// metronome/ui/legend.py.
struct LegendView: View {
    static let entries: [(control: String, description: String)] = [
        ("Click BPM number, or 0-9", "Start typing an exact BPM"),
        ("Enter", "Confirm typed BPM"),
        ("Esc", "Cancel typed BPM"),
        ("Space", "Start or stop the click"),
        ("Left / Right", "BPM -1 / +1"),
        ("Up / Down", "BPM -5 / +5"),
        ("N / M", "Beats per bar -1 / +1"),
        ("H or ?", "Toggle this help panel"),
    ]
    static let note = "Arrow keys and N / M can be held down to keep changing"

    let onDismiss: () -> Void

    var body: some View {
        ZStack {
            AppColor.overlayScrim
                .ignoresSafeArea()
                .contentShape(Rectangle())
                .onTapGesture(perform: onDismiss)

            VStack(spacing: 18) {
                Text("Controls")
                    .font(Config.font(Config.fontSizeLegendTitle, bold: true))
                    .foregroundStyle(AppColor.textPrimary)
                    .frame(maxWidth: .infinity, alignment: .leading)

                Grid(alignment: .leading, horizontalSpacing: 28, verticalSpacing: 8) {
                    ForEach(Self.entries, id: \.control) { entry in
                        GridRow {
                            Text(entry.control)
                                .font(Config.font(Config.fontSizeLegendBody))
                                .foregroundStyle(AppColor.accent)
                            Text(entry.description)
                                .font(Config.font(Config.fontSizeLegendBody))
                                .foregroundStyle(AppColor.textSecondary)
                        }
                    }
                }

                Text(Self.note)
                    .font(Config.font(Config.fontSizeLegendBody))
                    .foregroundStyle(AppColor.textSecondary)
                    .multilineTextAlignment(.center)

                Text("click anywhere or press H to close")
                    .font(Config.font(Config.fontSizeLegendBody))
                    .foregroundStyle(AppColor.textMuted)
            }
            .padding(24)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(AppColor.panel)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(AppColor.panelBorder, lineWidth: 1)
                    )
            )
            .padding(32)
        }
    }
}
