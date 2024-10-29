import 'client.dart';
import 'locate.dart';
import 'package:flutter/material.dart';
import 'main.dart';

class SignIn extends StatefulWidget {
  const SignIn({super.key, required this.title, this.newAccount = false});

  final String title;
  final bool newAccount;

  @override
  State<SignIn> createState() => _SignInState();
}

class _SignInState extends State<SignIn> {
  static String _signingStatus = "Input your Credentials";
  final TextEditingController _userController = TextEditingController();
  final TextEditingController _passController = TextEditingController();
  static TextEditingController? _confirmPassController;
  static bool inputsGood = true;
  final String specialChars = '[@, !, \$, _, -, ?, #, %, &]';

  void _createAccount() async {
    if (inputsGood) {
      setState(() {
        _signingStatus = "Creating Account...";
      });
      Map<String, dynamic> user = await Client.createAccount(
          _userController.text, _passController.text);
      //see if the user map contains the key 'detail'
      setState(() {
        if (user.containsKey('detail')) {
          _signingStatus = user['detail'];
        } else {
          _signingStatus =
              "Account creation successful!\n Returning to Sign In page in\n3.. 2.. 1..";
          Future.delayed(const Duration(seconds: 3), () {
            if (mounted) {
              Navigator.pop(context);
            }
          });
        }
      });
    } else {
      setState(() {
        _signingStatus =
            "Credentials must meet the requirements before submitting";
      });
    }
  }

  void _signIn() async {
    setState(() {
      _signingStatus = "Logging in...";
    });
    Map<String, dynamic> user =
        await Client.signIn(_userController.text, _passController.text);
    //see if the user map contains the key 'detail'
    setState(() {
      if (user.containsKey('detail')) {
        _signingStatus = user['detail'];
      } else {
        setState(() {
          _signingStatus = "Success!";
        });
        prefs.setString("username", _userController.text);
        _goToLocate(_userController.text);
      }
    });
  }

  void _goToLocate(String username) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => Locate(username: username)),
    );
  }

  void _loadAccount() async {
    final user = await prefs.getString('username');
    if (user != null) {
      _goToLocate(user);
    }
  }

  void _checkInputs() {
    setState(() {
      //First condition is of least importance, last is of most importance
      inputsGood = true;
      if (_passController.text != _confirmPassController?.text) {
        _signingStatus = "The passwords must match!";
        inputsGood = false;
      }

      if (!_passController.text.contains(RegExp(specialChars))) {
        _signingStatus = "Password must include at least one:\n$specialChars";
        inputsGood = false;
      }

      if (_passController.text.length < 8) {
        _signingStatus = "Password length must be at least 8 characters!";
        inputsGood = false;
      }

      if (_passController.text.length > 29) {
        _signingStatus = "Password must not be greater than 29 characters!";
        inputsGood = false;
      }

      if (_userController.text.length > 29) {
        _signingStatus = "Username must not be greater than 29 characters!";
        inputsGood = false;
      }

      if (_userController.text.isEmpty ||
          _passController.text.isEmpty ||
          _confirmPassController!.text.isEmpty) {
        _signingStatus = "Credentials must not be empty!";
        inputsGood = false;
      }

      if (inputsGood) {
        _signingStatus = "You beat the Password Game!\nHit submit to continue.";
      }
    });
  }

  @override
  void initState() {
    super.initState();
    setState(() {
      _signingStatus = "Input your Credentials";
    });
    if (widget.newAccount) {
      _confirmPassController = TextEditingController();
      _userController.addListener(_checkInputs);
      _passController.addListener(_checkInputs);
      _confirmPassController?.addListener(_checkInputs);
    } else {
      _loadAccount();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).primaryColor,
        title: Text("${widget.title} Page"),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Padding(
            padding: padding,
            child: Text(
              _signingStatus,
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ),
          _inputs(),
        ],
      ),
      persistentFooterButtons: [
        ElevatedButton(
            style: ElevatedButton.styleFrom(
              shape: BeveledRectangleBorder(
                borderRadius: BorderRadius.zero, //Rectangular border
              ),
              minimumSize: Size(double.infinity, 50),
            ),
            onPressed: widget.newAccount ? _createAccount : _signIn,
            child: Text(widget.newAccount ? "Create Account" : "Sign In"))
      ],
      persistentFooterAlignment: AlignmentDirectional.center,
    );
  }

  @override
  void dispose() {
    // Dispose the controllers when the widget is removed
    _userController.dispose();
    _passController.dispose();
    if (widget.newAccount) {
      _confirmPassController?.dispose();
    }
    super.dispose();
  }

  Center _inputs() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Padding(
            padding: padding,
            child: TextField(
              controller: _userController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Enter Username',
              ),
            ),
          ),
          Padding(
            padding: padding,
            child: TextField(
              controller: _passController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Enter Password',
              ),
              obscureText: true,
            ),
          ),
          if (widget.newAccount) ...[
            Padding(
              padding: padding,
              child: TextField(
                controller: _confirmPassController,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Confirm Password',
                ),
                obscureText: true,
              ),
            ),
          ]
        ],
      ),
    );
  }
}
