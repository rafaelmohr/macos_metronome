import XCTest
@testable import Metronome

final class MetronomeStateTests: XCTestCase {
    func testTempoClampsToRange() {
        let state = MetronomeState()
        state.setTempo(1000)
        XCTAssertEqual(state.tempo, Config.maxTempo)

        state.setTempo(-50)
        XCTAssertEqual(state.tempo, Config.minTempo)
    }

    func testAdjustTempo() {
        let state = MetronomeState()
        state.adjustTempo(5)
        XCTAssertEqual(state.tempo, Config.startTempo + 5)
    }

    func testIntervalMsMatchesTempo() {
        let state = MetronomeState()
        state.setTempo(120)
        XCTAssertEqual(state.intervalMs, 500)
    }

    func testBeatsPerBarClampsAndResetsBeat() {
        let state = MetronomeState()
        state.beat = 2

        state.adjustBeatsPerBar(100)
        XCTAssertEqual(state.beatsPerBar, Config.maxBeatsPerBar)
        XCTAssertEqual(state.beat, 0)

        state.beat = 0
        state.advanceBeat()
        state.adjustBeatsPerBar(-1000)
        XCTAssertEqual(state.beatsPerBar, Config.minBeatsPerBar)
        XCTAssertEqual(state.beat, 0)
    }

    func testAdvanceBeatWrapsAndReportsDownbeat() {
        let state = MetronomeState()
        state.beatsPerBar = 3

        XCTAssertFalse(state.advanceBeat()) // beat 1
        XCTAssertFalse(state.advanceBeat()) // beat 2
        XCTAssertTrue(state.advanceBeat())  // wraps to beat 0 - downbeat
    }

    func testTogglePause() {
        let state = MetronomeState()
        XCTAssertFalse(state.paused)
        state.togglePause()
        XCTAssertTrue(state.paused)
        state.togglePause()
        XCTAssertFalse(state.paused)
    }

    func testBpmEntryFlow() {
        let state = MetronomeState()
        state.startBpmEdit()
        XCTAssertTrue(state.editingBpm)

        state.appendBpmDigit("1")
        state.appendBpmDigit("4")
        state.appendBpmDigit("0")
        state.appendBpmDigit("9") // ignored past max digits
        XCTAssertEqual(state.bpmEntryBuffer, "140")

        state.backspaceBpmEdit()
        XCTAssertEqual(state.bpmEntryBuffer, "14")

        state.confirmBpmEdit()
        XCTAssertEqual(state.tempo, Config.minTempo) // 14 clamps to 20
        XCTAssertFalse(state.editingBpm)
        XCTAssertEqual(state.bpmEntryBuffer, "")
    }

    func testConfirmingEmptyBufferKeepsTempoUnchanged() {
        let state = MetronomeState()
        state.setTempo(90)
        state.startBpmEdit()
        state.confirmBpmEdit()
        XCTAssertEqual(state.tempo, 90)
    }

    func testCancelBpmEditDiscardsBuffer() {
        let state = MetronomeState()
        let originalTempo = state.tempo
        state.startBpmEdit()
        state.appendBpmDigit("9")
        state.appendBpmDigit("9")
        state.cancelBpmEdit()

        XCTAssertEqual(state.tempo, originalTempo)
        XCTAssertFalse(state.editingBpm)
        XCTAssertEqual(state.bpmEntryBuffer, "")
    }
}
