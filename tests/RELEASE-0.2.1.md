# v0.2.1 release verification

v0.2.1 is a distribution and ABI-documentation patch. It does not change the
frozen numerical implementation, scalar ABI, v1 batch runtime behavior, shared
symbol surface, or floating-point flags. It adds an explicit Apache-2.0 default
licence with upstream exceptions, installs the complete licence and ABI
document set, enforces every v1 field offset at compile time, and adds an
installed C++ consumer.

On 2026-08-18, release-preparation commit
`c91259b9906e8c7150e3bf6849c293b0a4f5eb31` was cloned locally with
`git clone --no-hardlinks` into a separate directory. The checkout reported no
tracked or untracked changes before configuration. The subsequent
evidence-only commit changes no library, build, test, licence, or ABI contract
content.

Acceptance required all eight CTest tests, including installed C, C++, Python,
R, and Julia consumers; the installed licence, notice, and ABI documents; the
three-symbol shared export audit; and the frozen 454-case exact probe hash.

All eight CTest tests passed in the clean checkout. The explicit differential
run reported 454 bit-identical cases with the frozen probe SHA-256:

```text
087532603ebd6d3addad5bec4d99290eb3f1a9ed82bdfb141d5e9708194235ff
```

The Apache-2.0 text produced SHA-256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.
The same tree passed GitHub Actions on Linux/GCC, macOS/AppleClang, and
Windows/MinGW in
[run 32127738223](https://github.com/zyf0717/lwbgt/actions/runs/32127738223).
