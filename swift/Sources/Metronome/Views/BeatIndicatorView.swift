import SwiftUI

/// The row of beat lights showing where we are in the bar.
/// Port of metronome/ui/beat_indicator.py.
struct BeatIndicatorView: View {
    let state: MetronomeState

    private let gap: CGFloat = 6

    var body: some View {
        GeometryReader { geo in
            let n = state.beatsPerBar
            let cellWidth = (geo.size.width - gap * CGFloat(n - 1)) / CGFloat(n)
            let radius = min(10, geo.size.height / 2)

            HStack(spacing: gap) {
                ForEach(0..<n, id: \.self) { i in
                    let isDownbeat = i == 0
                    let active = i == state.beat && !state.paused
                    let color: Color = active
                        ? (isDownbeat ? AppColor.beatDownbeatActive : AppColor.beatActive)
                        : AppColor.beatInactive

                    RoundedRectangle(cornerRadius: radius)
                        .fill(color)
                        .frame(width: cellWidth)
                        .overlay {
                            if cellWidth >= Config.minLabelCellWidth {
                                Text("\(i + 1)")
                                    .font(Config.font(Config.fontSizeSmall))
                                    .foregroundStyle(active ? AppColor.background : AppColor.textMuted)
                            }
                        }
                }
            }
        }
    }
}
