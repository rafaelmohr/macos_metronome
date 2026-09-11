import Foundation

/// Auto-repeat for held-down keys (e.g. arrow keys, N/M).
///
/// macOS's own key-repeat is a single global rate for every key, which
/// doesn't give us acceleration. Instead we track held keys ourselves: a key
/// fires once immediately, waits `keyRepeatInitialDelayMs`, then repeats at
/// `keyRepeatIntervalMs`, speeding up to `keyRepeatFastIntervalMs` after
/// `keyRepeatFastAfterMs` of continuous holding. Direct port of
/// metronome/key_repeater.py.
final class KeyRepeater {
    private struct HeldKey {
        let callback: () -> Void
        var heldMs: Double = 0
        var sinceRepeatMs: Double = 0
    }

    private var held: [UInt16: HeldKey] = [:]

    func press(_ key: UInt16, callback: @escaping () -> Void) {
        held[key] = HeldKey(callback: callback)
        callback()
    }

    func release(_ key: UInt16) {
        held.removeValue(forKey: key)
    }

    func update(dtMs: Double) {
        for key in held.keys {
            guard var state = held[key] else { continue }
            state.heldMs += dtMs
            state.sinceRepeatMs += dtMs
            held[key] = state

            guard state.heldMs >= Config.keyRepeatInitialDelayMs else { continue }

            let heldAfterDelay = state.heldMs - Config.keyRepeatInitialDelayMs
            let interval = heldAfterDelay >= Config.keyRepeatFastAfterMs
                ? Config.keyRepeatFastIntervalMs
                : Config.keyRepeatIntervalMs

            if state.sinceRepeatMs >= interval {
                held[key]?.sinceRepeatMs = 0
                state.callback()
            }
        }
    }
}
