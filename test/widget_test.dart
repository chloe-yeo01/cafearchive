import 'package:flutter_test/flutter_test.dart';

import 'package:cafearchive/main.dart';

void main() {
  testWidgets('App builds and shows camera button', (WidgetTester tester) async {
    await tester.pumpWidget(const CafeArchiveApp());
    expect(find.text('Take Photo'), findsOneWidget);
  });
}