import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Get available cameras
  final cameras = await availableCameras();
  runApp(
    ChangeNotifierProvider(
      create: (_) => CafeVisionService(cameras.first),
      child: const CafeArchiveApp(),
    ),
  );
}

class CafeArchiveApp extends StatelessWidget {
  const CafeArchiveApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CafeArchive',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.brown),
        useMaterial3: true,
      ),
      home: const CameraScreen(),
    );
  }
}

/// Service class for camera capture + backend communication
class CafeVisionService extends ChangeNotifier {
  final CameraDescription camera;
  String? lastResult;
  bool _loading = false;

  CafeVisionService(this.camera);

  bool get loading => _loading;

  // Mac IP on local network (update if your IP changes)
      static const String serverUrl = 'https://cafearchive.onrender.com';

  Future<void> analyzeImage(XFile image) async {
    _loading = true;
    notifyListeners();

    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$serverUrl/api/analyze'),
      );
      request.files.add(await http.MultipartFile.fromPath('file', image.path));
      final response = await request.send();
      final body = await response.stream.bytesToString();

      lastResult = body;
    } catch (e) {
      lastResult = 'Error: $e';
    }

    _loading = false;
    notifyListeners();
  }
}

/// Camera screen
class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    final service = context.read<CafeVisionService>();
    _controller = CameraController(service.camera, ResolutionPreset.medium);
    await _controller!.initialize();
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final service = context.watch<CafeVisionService>();

    if (_controller == null || !_controller!.value.isInitialized) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text('CafeArchive'),
        backgroundColor: Colors.brown.shade700,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          Expanded(
            child: CameraPreview(_controller!),
          ),
          if (service.loading)
            const LinearProgressIndicator()
          else if (service.lastResult != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: Colors.brown.shade50,
              child: Text(
                service.lastResult!,
                style: const TextStyle(fontSize: 14),
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton.icon(
                onPressed: service.loading ? null : () => _capture(service),
                icon: const Icon(Icons.camera_alt),
                label: const Text('Take Photo'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.brown,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _capture(CafeVisionService service) async {
    final controller = CameraController(service.camera, ResolutionPreset.medium);
    await controller.initialize();

    if (!mounted) return;

    final image = await controller.takePicture();
    await controller.dispose();

    if (!mounted) return;

    await service.analyzeImage(image);
  }
}