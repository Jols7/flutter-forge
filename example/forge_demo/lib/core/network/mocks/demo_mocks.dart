import 'mock_interceptor.dart';

/// Mirrors the saved examples of api/forge_demo.postman_collection.json
/// (fixtures in test/fixtures/). The demo API is fictional, so the app runs on mocks.
const demoMocks = <MockRoute>[
  MockRoute('GET', 'accounts', {
    'default': MockResponse(
      200,
      r'''{"data":[{"id":"acc_1","alias":"Nómina","number_masked":"•••• 4821","currency":"MXN","balance":15230.5,"type":"checking"},{"id":"acc_2","alias":null,"number_masked":"•••• 9034","currency":"USD","balance":820,"type":"savings"}]}''',
    ),
    'empty': MockResponse(200, r'''{"data":[]}'''),
    'offline': MockResponse(
      503,
      r'''{"code":"UNAVAILABLE","message":"Servicio no disponible"}''',
    ),
  }),
  MockRoute('GET', 'accounts/{accountId}/transactions', {
    'default': MockResponse(
      200,
      r'''{"data":[{"id":"tx_1","description":"Café","amount":-85.0,"currency":"MXN","booked_at":"2026-10-30T14:05:00Z","category":"food"},{"id":"tx_2","description":null,"amount":12000,"currency":"MXN","booked_at":"2026-10-29T09:00:00Z","category":null}],"next_page":null}''',
    ),
    'empty': MockResponse(200, r'''{"data":[],"next_page":null}'''),
  }),
];
