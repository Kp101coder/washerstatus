import 'dart:convert' as convert;
import 'package:http/http.dart' as http;

String _ip = "57.132.171.87:7106";
//String _ip = "10.148.109.161:7106";
// If you find this, please please dont blow my server up.
//I am just a humble noob creating his first flutter app and server

class Client {
  static Future<Map<String, dynamic>> get(String request) async {
    var response = await http.get(Uri.http(_ip, request));
    if (response.statusCode != 500) {
      return await convert.jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      return {"detail": "Server Error, Please try again"};
    }
  }

  static Future<List<Map<String, dynamic>>> getAll(String request) async {
    var response = await http.get(Uri.http(_ip, request));
    if (response.statusCode != 500) {
      return List<Map<String, dynamic>>.from(
          await convert.jsonDecode(response.body));
    } else {
      return [
        {"detail": "Server Error, Please try again"}
      ];
    }
  }

  static Future<Map<String, dynamic>> _put(String request) async {
    var response = await http.put(Uri.http(_ip, request));
    if (response.statusCode != 500) {
      return await convert.jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      return {"detail": "Server Error, Please try again"};
    }
  }

  static Future<Map<String, dynamic>> _post(
      String request, Map<String, dynamic> data) async {
    var response = await http.post(
      Uri.http(_ip, request), // Only the request path, no query parameters
      headers: <String, String>{
        'Content-Type':
            'application/json; charset=UTF-8', // Ensure correct content-type
      },
      body: convert.jsonEncode(data),
    );
    return convert.jsonDecode(response.body) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> signIn(String username, String password) {
    return _put("/users/$username/signin/$password");
  }

  static Future<Map<String, dynamic>> createAccount(
      String username, String password) {
    return _post("/users/", {"User Name": username, "User Password": password});
  }
}
