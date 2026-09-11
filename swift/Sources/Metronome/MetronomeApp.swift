import SwiftUI

/// This is a single-window utility app, not a document app - closing the
/// window (red button or Cmd+W) should quit, not leave a windowless app
/// running in the Dock.
final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        true
    }
}

@main
struct MetronomeApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate

    var body: some Scene {
        WindowGroup(Config.windowTitle) {
            ContentView()
        }
        .windowResizability(.contentSize)
    }
}
