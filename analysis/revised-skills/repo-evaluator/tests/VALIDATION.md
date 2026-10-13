# Local review edition validation

This is a local review edition, not an upstream release.
Run: python -B -m unittest discover -s tests -v
On the producing Windows/Python 3.13 host: 53 passed, 3 POSIX shell fixtures skipped.
The full review package also has separate mocked/inert portable-fetch, boundary,
junction, source-content suppression and scheduler tests. Those tests are not part
of this standalone skill archive; the tabbed review report includes their results.
No live target installation, live provider generation or hosted deployment was tested.
