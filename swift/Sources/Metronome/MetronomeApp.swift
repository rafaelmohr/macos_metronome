import SwiftUI

@main
struct MetronomeApp: App {
    var body: some Scene {
        WindowGroup(Config.windowTitle) {
            ContentView()
        }
        .windowResizability(.contentSize)
    }
}
