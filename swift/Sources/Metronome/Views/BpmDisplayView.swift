import SwiftUI

/// The big BPM number. Doubles as a click target that enters keyboard
/// text-entry mode (typed digits build a buffer, Enter confirms, Esc
/// cancels). Port of metronome/ui/bpm_display.py.
struct BpmDisplayView: View {
    let state: MetronomeState
    let onTap: () -> Void

    var body: some View {
        TimelineView(.periodic(from: .now, by: Config.cursorBlinkIntervalSeconds)) { timeline in
            let tick = Int(timeline.date.timeIntervalSinceReferenceDate / Config.cursorBlinkIntervalSeconds)
            let cursorVisible = tick % 2 == 0

            ZStack {
                if state.editingBpm {
                    RoundedRectangle(cornerRadius: 18)
                        .stroke(AppColor.editBorder, lineWidth: 2)
                }

                Text(displayText(cursorVisible: cursorVisible))
                    .font(Config.font(Config.fontSizeBpm, bold: true))
                    .foregroundStyle(state.editingBpm ? AppColor.accent : AppColor.textPrimary)
            }
            .frame(width: 340, height: 170)
            .contentShape(Rectangle())
            .onTapGesture(perform: onTap)
        }
    }

    private func displayText(cursorVisible: Bool) -> String {
        if state.editingBpm {
            return state.bpmEntryBuffer + (cursorVisible ? "|" : " ")
        }
        return "\(state.tempo)"
    }
}
