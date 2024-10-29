import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'sign_in.dart';
import 'package:video_player/video_player.dart';

final double padVal = 16.0;
final EdgeInsets padding = EdgeInsets.all(padVal);
final prefs = SharedPreferencesAsync();

void main() {
  runApp(const WelcomePage());
}

class WelcomePage extends StatelessWidget {
  const WelcomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Washer Status',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.orange.shade900),
        primaryColor: const Color.fromARGB(255, 193, 70, 3),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Login'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  late VideoPlayerController _controller;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.asset('assets/intro.mp4')
      ..initialize().then((_) {
        // Ensure the first frame is shown after the video is initialized, even before the play button has been pressed.
        setState(() {});
      });
    //_loadAccount(); Not needed as users should see my beautiful animation on startup
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _loadAccount() async {
    final prefs = SharedPreferencesAsync();
    final user = await prefs.getString('username');
    if (user != null) {
      Navigator.push(
        // ignore: use_build_context_synchronously
        context,
        MaterialPageRoute(builder: (context) => SignIn(title: "Sign In")),
      );
    }
  }

  void _goToSignIn(bool newAccount, bool pass) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SignIn(
          title: newAccount ? 'Sign Up' : 'Sign In',
          newAccount: newAccount,
        ),
      ),
    );
  }

  final ButtonStyle raisedButtonStyle = ElevatedButton.styleFrom(
    minimumSize: const Size(88, 36),
    padding: const EdgeInsets.symmetric(horizontal: 16),
    shape: const BeveledRectangleBorder(),
  );

  @override
  Widget build(BuildContext context) {
    Scaffold sc = Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).primaryColor,
        title: Text("${widget.title} Page"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'Welcome to',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            _controller.value.isInitialized
                ? AspectRatio(
                    aspectRatio: _controller.value.aspectRatio,
                    child: VideoPlayer(_controller),
                  )
                : Container(),
            Padding(
              padding: padding,
              child: ElevatedButton(
                onPressed: () => _goToSignIn(false, false),
                style: raisedButtonStyle,
                child: Text(
                  "Login",
                  style: Theme.of(context).textTheme.labelLarge,
                  selectionColor: Theme.of(context).focusColor,
                ),
              ),
            ),
            Padding(
              padding: padding,
              child: ElevatedButton(
                onPressed: () => _goToSignIn(true, false),
                style: raisedButtonStyle,
                child: Text(
                  "Sign Up",
                  style: Theme.of(context).textTheme.labelLarge,
                  selectionColor: Theme.of(context).focusColor,
                ),
              ),
            ),
          ],
        ),
      ),
    );
    _controller.play();
    return sc;
  }
}
