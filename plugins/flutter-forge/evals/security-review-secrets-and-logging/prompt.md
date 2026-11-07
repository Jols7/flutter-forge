---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Revisión de seguridad de este archivo de una app financiera Flutter:

```dart
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

const paymentsApiSecret = 'sk_live_EXAMPLE_NOT_REAL_KEY';

class SessionStore {
  Future<void> save(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
    print('saved token $token');
  }
}

final dio = Dio(BaseOptions(baseUrl: 'http://api.mybank.example/v1/'));
```
