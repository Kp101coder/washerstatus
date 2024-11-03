import 'dart:async';
import 'package:flutter/material.dart';
import 'client.dart';
import 'messager.dart';
import 'main.dart';

class MachineView extends StatefulWidget {
  const MachineView(
      {super.key,
      required this.username,
      required this.data,
      required this.floor});
  final String username;
  final Map<String, String> data;
  final String floor;

  @override
  State<MachineView> createState() => _MachineViewState();
}

class _MachineViewState extends State<MachineView> {
  // ignore: constant_identifier_names
  static const int _DELAY = 10;
  Timer? _timer; // Timer to periodically fetch data
  final List<Machine> _machines = [];

  @override
  void initState() {
    super.initState();
    _getMachines();
  }

  @override
  void dispose() {
    _timer
        ?.cancel(); // Cancel the timer when the widget is disposed to prevent memory leaks
    super.dispose();
  }

  void _goToPosts() {
    Navigator.push(
      context,
      MaterialPageRoute(
          builder: (context) => MessageView(
                username: widget.username,
                floorID: widget.data['floor']!,
                floor: widget.floor,
              )),
    );
  }

  void _getMachines() async {
    List<Map<String, dynamic>> machinesData =
        await Client.getAll("/rooms/${widget.data["Room"]}/machines");
    for (Map<String, dynamic> machine in machinesData) {
      _machines.add(Machine(
          doorOpen: machine["doorOpen"],
          hasClothes: machine["hasClothes"],
          timeRunning: machine["timeRun"],
          location: machine["relLoc"],
          lastUpdate: machine["lastUpdate"],
          isRunning: machine["isRunning"]));
    }
    _timer = Timer.periodic(const Duration(seconds: _DELAY), (timer) async {
      _updateStatus();
    });
  }

  void _updateStatus() async {
    List<Map<String, dynamic>> machinesData =
        await Client.getAll("/rooms/${widget.data["Room"]}/machines");
    setState(() {
      for (int i = 0; i < machinesData.length; i++) {
        Map<String, dynamic> machine = machinesData[i];
        _machines[i].doorOpen = machine["doorOpen"];
        _machines[i].hasClothes = machine["hasClothes"];
        _machines[i].timeRunning = machine["timeRun"];
        _machines[i].location = machine["relLoc"];
        _machines[i].lastUpdate = machine["lastUpdate"];
        _machines[i].isRunning = machine["isRunning"];
        if (_machines[i].isRunning) {
          _machines[i].color = Colors.red;
        } else if (_machines[i].hasClothes) {
          _machines[i].color = Colors.orange;
        } else if (_machines[i].doorOpen) {
          _machines[i].color = Colors.green;
        } else {
          _machines[i].color = Colors.yellow;
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).primaryColor,
        title: const Text("Machine View Page"),
      ),
      body: Column(
        children: <Widget>[
          SingleChildScrollView(
            child: Padding(
              padding: padding,
              child: Column(
                children: _machines.isNotEmpty
                    ? _machines.map((machine) {
                        return _makeContainer(machine);
                      }).toList()
                    : [
                        Text(
                          "Loading...",
                          style: Theme.of(context).textTheme.titleLarge,
                        )
                      ],
              ),
            ),
          ),
        ],
      ),
      persistentFooterButtons: [
        Padding(
          padding:
              EdgeInsets.fromLTRB(padVal / 8, padVal / 8, padVal / 8, padVal),
          child: ElevatedButton(
            style: ElevatedButton.styleFrom(
              shape: BeveledRectangleBorder(
                borderRadius: BorderRadius.zero, //Rectangular border
              ),
              minimumSize: Size(double.infinity, double.infinity),
            ),
            onPressed: _goToPosts,
            child: const Text("Floor Chat"),
          ),
        ),
      ],
      persistentFooterAlignment: AlignmentDirectional.center,
    );
  }

  Container _makeContainer(Machine machine) {
    return Container(
      padding: const EdgeInsets.all(8.0),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Image with conditional background
          Container(
            padding: const EdgeInsets.all(16.0),
            color: machine.color,
            child: Image.asset(
              "assets/washerIcon.png",
              width: 100, // Adjust width as needed
              height: 100, // Adjust height as needed
            ),
          ),
          const SizedBox(width: 10),
          // Text data to the right of the image
          Expanded(
              child: Column(children: [
            Text(
              machine.location,
              style: Theme.of(context).textTheme.titleMedium!.copyWith(
                    fontWeight: FontWeight.bold,
                    decoration: TextDecoration.underline,
                  ),
            ),
            Text(
              machine.timeLeft(),
              style: Theme.of(context).textTheme.labelLarge,
            ),
            Text(
              "Updated: ${machine.lastUpdate}",
              style: Theme.of(context).textTheme.labelLarge,
            ),
            Text(
              "Machine In Use: ${machine.isRunning}",
              style: Theme.of(context).textTheme.labelLarge,
            ),
            Text(
              "Machine Empty: ${!machine.hasClothes}",
              style: Theme.of(context).textTheme.labelLarge,
            ),
            Text(
              "Machine Door Open: ${machine.doorOpen}",
              style: Theme.of(context).textTheme.labelLarge,
            ),
          ])),
        ],
      ),
    );
  }
}

class Machine {
  Machine({
    required this.hasClothes,
    required this.isRunning,
    required this.doorOpen,
    required this.timeRunning,
    required this.lastUpdate,
    required this.location,
    this.color = Colors.green,
  });

  bool hasClothes;
  bool isRunning;
  bool doorOpen;
  int? timeRunning;
  String lastUpdate;
  String location;
  static const int approxTime = 50;
  MaterialColor color;

  String timeLeft() {
    if (timeRunning == null) {
      return "0 minutes";
    }
    int minLeft = (approxTime - timeRunning!);
    if (minLeft < 0) {
      minLeft *= -1;
      return "Overtime: $minLeft minutes";
    } else {
      return "Est. Time Left: $minLeft minutes";
    }
  }
}
