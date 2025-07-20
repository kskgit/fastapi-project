#!/usr/bin/env python3
"""
Clean Architecture依存関係チェッカー

各層が適切な依存関係を持っているかを検証します。
"""

import ast
from pathlib import Path


class DependencyChecker:
    """Clean Architecture依存関係チェッカー"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.violations: list[str] = []

        # Clean Architecture依存関係ルール
        self.allowed_dependencies = {
            "domain": set(),  # Domain層は何にも依存してはいけない
            "infrastructure": {"domain", "core"},  # Infrastructure層の依存
            "services": {"domain"},  # Services層はDomain層のみに依存
            "api": {"domain", "services"},  # API層はDomainとServices層に依存
            "core": set(),  # Core層は共通ユーティリティなので依存なし
        }

    def check_imports_in_file(self, file_path: Path) -> set[str]:
        """ファイル内のimportをチェックして依存関係を抽出"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)

            return imports
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return set()

    def get_layer_from_import(self, import_name: str) -> str | None:
        """importからレイヤーを特定"""
        if import_name.startswith("app.") and not import_name.startswith("app.clean."):
            parts = import_name.split(".")
            if len(parts) >= 2:
                return parts[1]  # app.{layer}
        return None

    def check_layer_dependencies(self, layer: str) -> None:
        """指定されたレイヤーの依存関係をチェック"""
        layer_path = self.project_root / "app" / layer

        if not layer_path.exists():
            return

        print(f"Checking {layer} layer dependencies...")

        # レイヤー内のすべてのPythonファイルをチェック
        for py_file in layer_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            imports = self.check_imports_in_file(py_file)

            for import_name in imports:
                imported_layer = self.get_layer_from_import(import_name)

                if imported_layer and imported_layer != layer:
                    # 依存関係チェック
                    allowed = self.allowed_dependencies.get(layer, set())

                    if imported_layer not in allowed:
                        violation = (
                            f"❌ VIOLATION: {layer} layer cannot depend on "
                            f"{imported_layer} layer\n"
                            f"   File: {py_file.relative_to(self.project_root)}\n"
                            f"   Import: {import_name}\n"
                            f"   Allowed dependencies for {layer}: {allowed or 'None'}"
                        )
                        self.violations.append(violation)
                        print(violation)
                    else:
                        print(f"✅ OK: {layer} -> {imported_layer} (allowed)")

    def check_all_layers(self) -> bool:
        """すべてのレイヤーの依存関係をチェック"""
        print("🔍 Checking Clean Architecture dependency rules...\n")

        for layer in self.allowed_dependencies.keys():
            self.check_layer_dependencies(layer)
            print()

        # 結果サマリー
        if self.violations:
            print(f"❌ Found {len(self.violations)} dependency violations:")
            for violation in self.violations:
                print(violation)
                print()
            return False
        else:
            print("✅ All dependency rules are satisfied!")
            print("\nClean Architecture dependency rules:")
            for layer, deps in self.allowed_dependencies.items():
                deps_str = ", ".join(deps) if deps else "None"
                print(f"  • {layer}: can depend on [{deps_str}]")
            return True


def main() -> None:
    """メイン実行関数"""
    project_root = Path(__file__).parent.parent
    checker = DependencyChecker(project_root)

    success = checker.check_all_layers()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
