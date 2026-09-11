import Foundation

/// Drives the beat tick with a precise, low-jitter repeating timer.
///
/// Recreated (via `start`) whenever the tempo changes, mirroring
/// `App._reset_timer` in the Python version. Ticks fire on a background
/// queue and hop to the main actor before touching `onTick`, since that
/// closure mutates observable state and triggers UI updates.
final class MetronomeClock {
    private var timer: DispatchSourceTimer?
    private let queue = DispatchQueue(label: "com.metronome.clock", qos: .userInteractive)

    var onTick: (() -> Void)?

    func start(intervalMs: Int) {
        stop()
        let source = DispatchSource.makeTimerSource(queue: queue)
        source.schedule(
            deadline: .now() + .milliseconds(intervalMs),
            repeating: .milliseconds(intervalMs),
            leeway: .milliseconds(1)
        )
        source.setEventHandler { [weak self] in
            DispatchQueue.main.async {
                self?.onTick?()
            }
        }
        source.resume()
        timer = source
    }

    func stop() {
        timer?.cancel()
        timer = nil
    }
}
