import 'dart:convert';
import 'dart:io';

/// Reads a JSON fixture written by forge-api-contract: `fixture('accounts/list_transactions_200.json')`.
Map<String, dynamic> fixture(String path) =>
    jsonDecode(File('test/fixtures/$path').readAsStringSync())
        as Map<String, dynamic>;
