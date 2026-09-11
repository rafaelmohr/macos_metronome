import AppKit
import SwiftUI

/// Virtual key codes (physical key position, independent of keyboard
/// layout - the same property pygame's K_* constants have). Standard macOS
/// kVK_* values.
private enum KeyCode {
    static let space: UInt16 = 49
    static let left: UInt16 = 123
    static let right: UInt16 = 124
    static let down: UInt16 = 125
    static let up: UInt16 = 126
    static let n: UInt16 = 45
    static let m: UInt16 = 46
    static let h: UInt16 = 4
    static let slash: UInt16 = 44
    static let returnKey: UInt16 = 36
    static let keypadEnter: UInt16 = 76
    static let escape: UInt16 = 53
    static let delete: UInt16 = 51

    // Top-row digits and keypad digits both map to their character.
    static let digits: [UInt16: String] = [
        29: "0", 18: "1", 19: "2", 20: "3", 21: "4",
        23: "5", 22: "6", 26: "7", 28: "8", 25: "9",
        82: "0", 83: "1", 84: "2", 85: "3", 86: "4",
        87: "5", 88: "6", 91: "7", 89: "8", 92: "9",
    ]
}

/// Composes the three widgets, owns the event loop equivalents (key
/// monitor, beat clock, key-repeat ticker) and routes input exactly like
/// metronome/app.py's App class.
struct ContentView: View {
    @State private var state = MetronomeState()
    @State private var legendVisible = false

    private let audio = AudioEngine()
    private let clock = MetronomeClock()
    private let keyRepeater = KeyRepeater()

    @State private var keyMonitor: Any?
    @State private var repeaterTimer: Timer?
    @State private var lastRepeaterTick = Date()
    @State private var bpmAutoConfirmTimer: Timer?

    var body: some View {
        ZStack {
            AppColor.background
                .ignoresSafeArea()
                .contentShape(Rectangle())
                .onTapGesture(perform: dismissEditIfNeeded)

            VStack(spacing: 0) {
                Spacer().frame(height: 50)
                BpmDisplayView(state: state, onTap: handleBpmTap)
                Spacer().frame(height: 30)
                BeatIndicatorView(state: state)
                    .frame(height: 56)
                    .padding(.horizontal, 40)
                Spacer()
            }

            if state.paused {
                VStack {
                    Spacer().frame(height: 322)
                    Text("PAUSED")
                        .font(Config.font(Config.fontSizeSmall))
                        .foregroundStyle(AppColor.pause)
                    Spacer()
                }
            }

            VStack {
                Spacer()
                Text("Press H for controls")
                    .font(Config.font(Config.fontSizeHint))
                    .foregroundStyle(AppColor.textMuted)
                    .padding(.bottom, 14)
            }

            if legendVisible {
                LegendView(onDismiss: { legendVisible = false })
            }
        }
        .frame(width: Config.windowWidth, height: Config.windowHeight)
        .background(AppColor.background)
        .onAppear(perform: setUp)
        .onDisappear(perform: tearDown)
    }

    // --- setup ---
    private func setUp() {
        clock.onTick = handleTick
        clock.start(intervalMs: state.intervalMs)

        keyMonitor = NSEvent.addLocalMonitorForEvents(matching: [.keyDown, .keyUp]) { event in
            if event.type == .keyDown {
                handleKeyDown(event)
            } else {
                keyRepeater.release(event.keyCode)
            }
            return nil
        }

        lastRepeaterTick = Date()
        repeaterTimer = Timer.scheduledTimer(withTimeInterval: 1.0 / 60.0, repeats: true) { _ in
            let now = Date()
            let dtMs = now.timeIntervalSince(lastRepeaterTick) * 1000
            lastRepeaterTick = now
            keyRepeater.update(dtMs: dtMs)
        }
    }

    private func tearDown() {
        clock.stop()
        if let keyMonitor {
            NSEvent.removeMonitor(keyMonitor)
        }
        repeaterTimer?.invalidate()
        bpmAutoConfirmTimer?.invalidate()
    }

    // --- callbacks ---
    private func handleTick() {
        guard !state.paused else { return }
        let isDownbeat = state.advanceBeat()
        audio.playBeat(isDownbeat: isDownbeat)
    }

    private func resetClock() {
        clock.start(intervalMs: state.intervalMs)
    }

    private func nudgeTempo(_ delta: Int) {
        state.adjustTempo(delta)
        resetClock()
    }

    // --- BPM edit auto-confirm ---
    // Typing a BPM and then walking away shouldn't leave it stuck in edit
    // mode forever - confirm automatically after a short pause in typing.
    private func scheduleAutoConfirm() {
        bpmAutoConfirmTimer?.invalidate()
        bpmAutoConfirmTimer = Timer.scheduledTimer(
            withTimeInterval: Config.bpmAutoConfirmDelaySeconds, repeats: false
        ) { _ in
            guard state.editingBpm else { return }
            state.confirmBpmEdit()
            resetClock()
        }
    }

    private func cancelAutoConfirm() {
        bpmAutoConfirmTimer?.invalidate()
        bpmAutoConfirmTimer = nil
    }

    // --- mouse ---
    private func handleBpmTap() {
        if state.editingBpm {
            cancelAutoConfirm()
            state.confirmBpmEdit()
            resetClock()
        } else {
            state.startBpmEdit()
            scheduleAutoConfirm()
        }
    }

    private func dismissEditIfNeeded() {
        if state.editingBpm {
            cancelAutoConfirm()
            state.confirmBpmEdit()
            resetClock()
        }
    }

    // --- keyboard ---
    private func handleKeyDown(_ event: NSEvent) {
        if event.isARepeat { return }
        let code = event.keyCode

        if state.editingBpm {
            handleBpmEntryKey(code)
            return
        }

        switch code {
        case KeyCode.space:
            state.togglePause()
        case KeyCode.right:
            keyRepeater.press(code) { nudgeTempo(Config.tempoStepSmall) }
        case KeyCode.left:
            keyRepeater.press(code) { nudgeTempo(-Config.tempoStepSmall) }
        case KeyCode.up:
            keyRepeater.press(code) { nudgeTempo(Config.tempoStepLarge) }
        case KeyCode.down:
            keyRepeater.press(code) { nudgeTempo(-Config.tempoStepLarge) }
        case KeyCode.m:
            keyRepeater.press(code) { state.adjustBeatsPerBar(1) }
        case KeyCode.n:
            keyRepeater.press(code) { state.adjustBeatsPerBar(-1) }
        case KeyCode.h, KeyCode.slash:
            legendVisible.toggle()
        default:
            if let digit = KeyCode.digits[code] {
                state.startBpmEdit()
                state.appendBpmDigit(digit)
                scheduleAutoConfirm()
            }
        }
    }

    private func handleBpmEntryKey(_ code: UInt16) {
        switch code {
        case KeyCode.returnKey, KeyCode.keypadEnter:
            cancelAutoConfirm()
            state.confirmBpmEdit()
        case KeyCode.escape:
            cancelAutoConfirm()
            state.cancelBpmEdit()
        case KeyCode.delete:
            state.backspaceBpmEdit()
            scheduleAutoConfirm()
        default:
            guard let digit = KeyCode.digits[code] else { return }
            state.appendBpmDigit(digit)
            scheduleAutoConfirm()
        }
        resetClock()
    }
}
