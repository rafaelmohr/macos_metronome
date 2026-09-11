import Observation

/// Mutable application state and the rules for changing it.
///
/// Nothing in here touches SwiftUI views directly - this is the single
/// source of truth for "what is the metronome currently doing", so views can
/// stay dumb (render whatever the state says) and input code can stay dumb
/// (translate raw events into calls on this class). Direct port of
/// metronome/state.py.
@Observable
final class MetronomeState {
    var tempo = Config.startTempo
    var beatsPerBar = Config.startBeatsPerBar
    var beat = 0
    var paused = false

    // BPM keyboard text-entry mode
    var editingBpm = false
    var bpmEntryBuffer = ""

    // --- tempo ---
    var intervalMs: Int { 60000 / tempo }

    func adjustTempo(_ delta: Int) {
        setTempo(tempo + delta)
    }

    func setTempo(_ value: Int) {
        tempo = max(Config.minTempo, min(Config.maxTempo, value))
    }

    // --- time signature ---
    func adjustBeatsPerBar(_ delta: Int) {
        beatsPerBar = max(Config.minBeatsPerBar, min(Config.maxBeatsPerBar, beatsPerBar + delta))
        beat = 0
    }

    // --- transport ---
    func togglePause() {
        paused.toggle()
    }

    /// Move to the next beat, returning true if it's the downbeat.
    @discardableResult
    func advanceBeat() -> Bool {
        beat = (beat + 1) % beatsPerBar
        return beat == 0
    }

    // --- BPM keyboard text-entry ---
    func startBpmEdit() {
        editingBpm = true
        bpmEntryBuffer = ""
    }

    func appendBpmDigit(_ digit: String) {
        if bpmEntryBuffer.count < Config.bpmEntryMaxDigits {
            bpmEntryBuffer += digit
        }
    }

    func backspaceBpmEdit() {
        if !bpmEntryBuffer.isEmpty {
            bpmEntryBuffer.removeLast()
        }
    }

    func confirmBpmEdit() {
        if let value = Int(bpmEntryBuffer) {
            setTempo(value)
        }
        editingBpm = false
        bpmEntryBuffer = ""
    }

    func cancelBpmEdit() {
        editingBpm = false
        bpmEntryBuffer = ""
    }
}
