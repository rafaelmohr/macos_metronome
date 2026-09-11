// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "Metronome",
    platforms: [.macOS(.v14)],
    targets: [
        .executableTarget(
            name: "Metronome",
            resources: [
                .copy("Resources/high.wav"),
                .copy("Resources/low.wav"),
            ]
        ),
        .testTarget(
            name: "MetronomeTests",
            dependencies: ["Metronome"]
        ),
    ]
)
