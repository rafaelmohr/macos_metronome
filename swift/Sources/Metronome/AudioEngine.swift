import AVFoundation

/// Click-sound loading and playback.
///
/// Uses AVAudioEngine with one AVAudioPlayerNode per sound (rather than a
/// single AVAudioPlayer) so a retriggered click at high tempos doesn't cut
/// off a click that's still finishing - matching pygame.mixer.Sound.play(),
/// which allocates a fresh channel per call.
final class AudioEngine {
    private let engine = AVAudioEngine()
    private let highPlayer = AVAudioPlayerNode()
    private let lowPlayer = AVAudioPlayerNode()
    private var highBuffer: AVAudioPCMBuffer?
    private var lowBuffer: AVAudioPCMBuffer?

    init(highFile: String = "high", lowFile: String = "low") {
        highBuffer = Self.loadBuffer(named: highFile)
        lowBuffer = Self.loadBuffer(named: lowFile)

        engine.attach(highPlayer)
        engine.attach(lowPlayer)

        if let format = highBuffer?.format {
            engine.connect(highPlayer, to: engine.mainMixerNode, format: format)
        }
        if let format = lowBuffer?.format {
            engine.connect(lowPlayer, to: engine.mainMixerNode, format: format)
        }

        try? engine.start()
        highPlayer.play()
        lowPlayer.play()
    }

    func playBeat(isDownbeat: Bool) {
        if isDownbeat, let buffer = highBuffer {
            highPlayer.scheduleBuffer(buffer, at: nil, options: [.interrupts])
        } else if let buffer = lowBuffer {
            lowPlayer.scheduleBuffer(buffer, at: nil, options: [.interrupts])
        }
    }

    private static func loadBuffer(named name: String) -> AVAudioPCMBuffer? {
        guard let url = Bundle.module.url(forResource: name, withExtension: "wav"),
              let file = try? AVAudioFile(forReading: url),
              let buffer = AVAudioPCMBuffer(
                pcmFormat: file.processingFormat,
                frameCapacity: AVAudioFrameCount(file.length)
              )
        else { return nil }

        try? file.read(into: buffer)
        return buffer
    }
}
