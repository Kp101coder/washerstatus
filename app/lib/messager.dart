import 'package:flutter/material.dart';

class MessageView extends StatefulWidget {
  const MessageView(
      {super.key,
      required this.username,
      required this.floorID,
      required this.floor});
  final String username;
  final String floorID;
  final String floor;

  @override
  State<MessageView> createState() => _MessageViewState();
}

class _MessageViewState extends State<MessageView> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).primaryColor,
        title: const Text("Floor Posts Page"),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Text(widget.username),
          Text(widget.floor),
          Text(widget.floorID),
        ],
      ),
      persistentFooterButtons: [],
      persistentFooterAlignment: AlignmentDirectional.center,
    );
  }
}
