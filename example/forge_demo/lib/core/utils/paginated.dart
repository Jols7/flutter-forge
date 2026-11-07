/// A page of results. Named `Paginated` to avoid clashing with Flutter's `Page`.
class Paginated<T> {
  const Paginated({required this.items, required this.nextPage});

  final List<T> items;
  final int? nextPage;

  bool get hasMore => nextPage != null;
}
