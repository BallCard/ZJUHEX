"""
Quick syntax and import validation for async_extractor implementation.

Checks:
1. Python syntax is valid
2. Imports are correct
3. Class structure is sound
"""

import sys
import ast
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def check_syntax(file_path):
    """Check if Python file has valid syntax."""
    print(f"\n[Checking] {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        ast.parse(code)
        print("  ✓ Syntax valid")
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error: {e}")
        return False


def check_class_structure(file_path, expected_class, expected_methods):
    """Check if class has expected methods."""
    print(f"\n[Checking] Class structure in {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        tree = ast.parse(code)

        # Find class
        class_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == expected_class:
                class_node = node
                break

        if not class_node:
            print(f"  ✗ Class '{expected_class}' not found")
            return False

        print(f"  ✓ Class '{expected_class}' found")

        # Check methods
        methods = [n.name for n in class_node.body if isinstance(n, ast.FunctionDef)]

        for method in expected_methods:
            if method in methods:
                print(f"    ✓ Method '{method}' exists")
            else:
                print(f"    ✗ Method '{method}' missing")
                return False

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def check_imports(file_path, expected_imports):
    """Check if file has expected imports."""
    print(f"\n[Checking] Imports in {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        tree = ast.parse(code)

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

        for expected in expected_imports:
            found = any(expected in imp for imp in imports)
            if found:
                print(f"  ✓ Import '{expected}' found")
            else:
                print(f"  ✗ Import '{expected}' missing")
                return False

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("Quick Validation: Async Extractor Implementation")
    print("=" * 60)

    base_path = Path(__file__).parent

    # Check async_extractor.py
    async_extractor_path = base_path / "src" / "backend" / "services" / "async_extractor.py"

    results = []

    # 1. Syntax check
    results.append(check_syntax(async_extractor_path))

    # 2. Class structure check
    results.append(check_class_structure(
        async_extractor_path,
        "AsyncExtractor",
        ["__init__", "extract_chunk", "extract_batch", "_update_progress"]
    ))

    # 3. Import check
    results.append(check_imports(
        async_extractor_path,
        ["json", "pathlib", "datetime", "knowledge_graph", "paths"]
    ))

    # Check main.py modifications
    main_path = base_path / "src" / "backend" / "main.py"

    # 4. Syntax check
    results.append(check_syntax(main_path))

    # 5. Import check
    results.append(check_imports(
        main_path,
        ["BackgroundTasks", "AsyncExtractor"]
    ))

    # 6. Check for new functions
    print(f"\n[Checking] Functions in {main_path}")
    try:
        with open(main_path, 'r', encoding='utf-8') as f:
            code = f.read()

        tree = ast.parse(code)
        functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

        expected_functions = ["build_graph_task", "update_job_state", "get_progress"]
        for func in expected_functions:
            if func in functions:
                print(f"  ✓ Function '{func}' exists")
                results.append(True)
            else:
                print(f"  ✗ Function '{func}' missing")
                results.append(False)

    except Exception as e:
        print(f"  ✗ Error: {e}")
        results.append(False)

    # Summary
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All checks passed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start backend: uvicorn src.backend.main:app --reload")
        print("3. Run integration test: python test_integration_async.py")
        return 0
    else:
        print(f"✗ {results.count(False)} check(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
