import 'dart:convert';

import 'package:app/machine_view.dart';
import 'package:flutter/material.dart';
import 'client.dart';
import 'main.dart';

class Locate extends StatefulWidget {
  const Locate({super.key, required this.username});
  final String username;

  @override
  State<Locate> createState() => _LocateState();
}

class _LocateState extends State<Locate> {
  final List<Item> _dropdowns = [];
  Map<String, String> data = {};
  final List<String> _itemNames = [
    "Organization",
    "Location",
    "Building",
    "Floor",
    "Room",
  ];
  String floor = "";
  int _itemIndex = 0;
  bool _buttonShow = false;

  @override
  void initState() {
    super.initState();
    _loadData();
    _initializeDropdowns();
  }

  void _loadData() async {
    if (await prefs.containsKey("data")) {
      final Map<String, dynamic> dynamicMap = jsonDecode((await prefs.getString("data"))!);
      // Convert the dynamic map to a map with String values
      data = dynamicMap.map((key, value) => MapEntry(key, value.toString()));
      _goToMachines();
    }
  }

  void _initializeDropdowns() async {
    final orgMap = await _fetchOptions("/organizations/all");
    setState(() {
      _dropdowns.add(Item(
        expandedValue:
            "Choose your affiliated university. Type University to see options.",
        key: _itemNames[_itemIndex],
        icon: const Icon(Icons.groups),
        options: orgMap,
      ));
    });
  }

  Future<Map<String, String>> _fetchOptions(String endpoint) async {
    final List<Map<String, dynamic>> allData = await Client.getAll(endpoint);
    Map<String, String> outputData = {};
    for (Map<String, dynamic> entry in allData) {
      String name = "";
      String id = "";
      for (String key in entry.keys) {
        if (key.toLowerCase().contains("name")) {
          name = entry[key].toString();
        } else if (key.toLowerCase() == "id") {
          id = entry[key].toString();
        }

        if (name != "" && id != "") {
          break;
        }
      }
      outputData[name] = id;
    }
    return outputData;
  }

  Autocomplete<String> _input(Item item) {
    return Autocomplete<String>(
      optionsBuilder: (TextEditingValue textEditingValue) {
        if (textEditingValue.text.isEmpty) {
          return const Iterable<String>.empty();
        }
        return item.options.keys.where((String option) {
          return option
              .toLowerCase()
              .contains(textEditingValue.text.toLowerCase());
        });
      },
      onSelected: (String selection) async {
        data[item.key] = item.options[selection]!;
        item.isExpanded = false;
        //Set the floor to the selection if currently on floor
        if (_itemNames[_itemIndex] == "Floor") {
          floor = selection;
        }
        //If this dropdown has been edited, all its sucessors must be reset
        if (_itemNames.indexOf(item.key) != _itemIndex) {
          setState(() {
            int originalLength = _dropdowns.length;
            for (int i = _itemNames.indexOf(item.key) + 1;
                i < originalLength;
                i++) {
              data.remove(_dropdowns.removeLast().key);
              _itemIndex--;
            }
          });
        }
        //Add the dropdown if there are still more. Otherwise show next page button
        if (_itemIndex < _itemNames.length - 1) {
          _itemIndex++;
          await _addNextDropdown(_itemNames[_itemIndex]);
        } else {
          setState(() {
            _buttonShow = true;
          });
        }
      },
    );
  }

  Future<void> _addNextDropdown(String currentKey) async {
    String? endpoint;
    String expandedText;
    Icon icon;

    switch (currentKey) {
      case "Location":
        endpoint = "/organizations/${data['Organization']}/locations";
        expandedText =
            "Choose your campus location. Type campus to see options.";
        icon = const Icon(Icons.location_on_outlined);
        break;
      case "Building":
        endpoint = "/locations/${data['Location']}/buildings";
        expandedText = "Choose your residence building.";
        icon = const Icon(Icons.business);
        break;
      case "Floor":
        endpoint = "/buildings/${data['Building']}/floors";
        expandedText = "Choose your floor.";
        icon = const Icon(Icons.layers);
        break;
      case "Room":
        endpoint = "/floors/${data['Floor']}/rooms";
        expandedText = "Choose your Room. Type room to see options.";
        icon = const Icon(Icons.account_tree_outlined);
        break;
      default:
        return;
    }

    final options = await _fetchOptions(endpoint);
    setState(() {
      _dropdowns.add(Item(
        expandedValue: expandedText,
        key: currentKey,
        icon: icon,
        options: options,
      ));
    });
  }

  void _goToMachinesButton() {
    prefs.setString("data", jsonEncode(data));
    _goToMachines();
  }

  void _goToMachines() {
    Navigator.push(
      context,
      MaterialPageRoute(
          builder: (context) =>
              MachineView(username: widget.username, data: data, floor: floor)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).primaryColor,
        title: const Text("Location Data Page"),
      ),
      body: SingleChildScrollView(
        child: _buildPanel(),
      ),
      persistentFooterButtons: [
        Visibility(
          visible: _buttonShow,
          child: ElevatedButton(
            style: ElevatedButton.styleFrom(
              shape: BeveledRectangleBorder(
                borderRadius: BorderRadius.zero, //Rectangular border
              ),
              minimumSize: Size(double.infinity, 50),
            ),
            onPressed: _goToMachinesButton,
            child: const Text("View Machines"),
          ),
        ),
      ],
      persistentFooterAlignment: AlignmentDirectional.center,
    );
  }

  Widget _buildPanel() {
    return ExpansionPanelList(
      expansionCallback: (int index, bool isExpanded) {
        setState(() {
          _dropdowns[index].isExpanded = isExpanded;
        });
      },
      children: _dropdowns.map<ExpansionPanel>((Item item) {
        return ExpansionPanel(
          headerBuilder: (BuildContext context, bool isExpanded) {
            return ListTile(title: Text(item.headerValue));
          },
          body: ListTile(
            title: Text(item.expandedValue),
            subtitle: _input(item),
            trailing: item.icon,
          ),
          isExpanded: item.isExpanded,
        );
      }).toList(),
    );
  }
}

class Item {
  Item({
    required this.expandedValue,
    required this.key,
    required this.icon,
    required this.options,
    this.isExpanded = true,
  }) : headerValue = "Select $key";

  String expandedValue;
  String headerValue;
  String key;
  bool isExpanded;
  Icon icon;
  Map<String, String> options;
}
