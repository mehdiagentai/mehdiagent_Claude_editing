// Person matte for the presenter: Apple Vision segmentation, one 8-bit mask per video frame.
// usage: personmask <video> <outW> <outH> [person|subject] [frameStep]  -> raw gray8 frames on stdout
// person  = VNGeneratePersonSegmentationRequest (.accurate)  — soft hair edges, may drop a held prop
// subject = VNGenerateForegroundInstanceMaskRequest           — keeps held objects (mic), harder edges
import AVFoundation
import Vision
import CoreImage
import Foundation

let a = CommandLine.arguments
let url = URL(fileURLWithPath: a[1])
let W = Int(a[2])!, H = Int(a[3])!
let mode = a.count > 4 ? a[4] : "person"
let step = a.count > 5 ? Int(a[5])! : 1
let ctx = CIContext(options: [.workingColorSpace: NSNull()])
let asset = AVURLAsset(url: url)
let track = asset.tracks(withMediaType: .video)[0]
let reader = try! AVAssetReader(asset: asset)
let out = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
out.alwaysCopiesSampleData = false
reader.add(out); reader.startReading()
let personReq = VNGeneratePersonSegmentationRequest()
personReq.qualityLevel = .accurate
personReq.outputPixelFormat = kCVPixelFormatType_OneComponent8
var buf = [UInt8](repeating: 0, count: W * H)
let stdout = FileHandle.standardOutput
var i = 0
while let sb = out.copyNextSampleBuffer() {
    defer { i += 1 }
    if i % step != 0 { continue }
    guard let pb = CMSampleBufferGetImageBuffer(sb) else { continue }
    var maskCI: CIImage? = nil
    let h = VNImageRequestHandler(cvPixelBuffer: pb, options: [:])
    if mode == "subject" {
        let r = VNGenerateForegroundInstanceMaskRequest()
        try? h.perform([r])
        if let o = r.results?.first, let m = try? o.generateScaledMaskForImage(forInstances: o.allInstances, from: h) {
            maskCI = CIImage(cvPixelBuffer: m)
        }
    } else {
        try? h.perform([personReq])
        if let m = personReq.results?.first?.pixelBuffer { maskCI = CIImage(cvPixelBuffer: m) }
    }
    if let m = maskCI {
        let sx = CGFloat(W) / m.extent.width, sy = CGFloat(H) / m.extent.height
        let scaled = m.transformed(by: CGAffineTransform(scaleX: sx, y: sy))
        buf.withUnsafeMutableBytes { p in
            ctx.render(scaled, toBitmap: p.baseAddress!, rowBytes: W, bounds: CGRect(x: 0, y: 0, width: W, height: H),
                       format: .L8, colorSpace: nil)
        }
    } else {
        for k in 0..<buf.count { buf[k] = 0 }
    }
    stdout.write(Data(buf))
}
