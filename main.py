"""CSVファイル結合アプリケーションのエントリーポイント

このモジュールは、複数のCSVファイルを結合するCLIアプリケーションです。
"""
import argparse
import sys
from pathlib import Path
import logging

from usecase.merge_csv_files import MergeCsvFilesUseCase


# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数を解析
    
    Returns:
        解析された引数
    """
    parser = argparse.ArgumentParser(
        description="複数のCSVファイルを結合します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py
  python main.py --input time_case --output static/downloads
  python main.py --help
        """
    )
    
    parser.add_argument(
        "--input",
        type=str,
        default="time_case",
        help="入力CSVファイルが格納されているディレクトリ（デフォルト: time_case）"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="static/downloads",
        help="結合後のCSVファイルを保存するディレクトリ（デフォルト: static/downloads）"
    )
    
    return parser.parse_args()


def get_csv_files(input_dir: Path) -> list[Path]:
    """指定されたディレクトリ内のすべてのCSVファイルを取得
    
    Args:
        input_dir: 入力ディレクトリ
        
    Returns:
        CSVファイルのパスリスト
        
    Raises:
        FileNotFoundError: ディレクトリが存在しない場合
        ValueError: CSVファイルが見つからない場合
    """
    if not input_dir.exists():
        raise FileNotFoundError(f"入力ディレクトリが見つかりません: {input_dir}")
    
    if not input_dir.is_dir():
        raise ValueError(f"指定されたパスはディレクトリではありません: {input_dir}")
    
    csv_files = sorted(input_dir.glob("*.csv"))
    
    if not csv_files:
        raise ValueError(f"CSVファイルが見つかりませんでした: {input_dir}")
    
    return csv_files


def main() -> int:
    """メイン関数
    
    Returns:
        終了コード（成功: 0、失敗: 1）
    """
    try:
        # コマンドライン引数を解析
        args = parse_arguments()
        
        # パスを作成
        input_dir = Path(args.input)
        output_dir = Path(args.output)
        
        logger.info("=" * 60)
        logger.info("CSVファイル結合処理を開始します")
        logger.info("=" * 60)
        logger.info(f"入力ディレクトリ: {input_dir.absolute()}")
        logger.info(f"出力ディレクトリ: {output_dir.absolute()}")
        
        # 出力ディレクトリを作成（存在しない場合）
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"出力ディレクトリを準備しました: {output_dir}")
        
        # CSVファイルを取得
        csv_files = get_csv_files(input_dir)
        logger.info(f"入力CSVファイル数: {len(csv_files)}")
        for i, csv_file in enumerate(csv_files, 1):
            logger.info(f"  {i}. {csv_file.name}")
        
        # UseCaseを実行
        logger.info("-" * 60)
        logger.info("結合処理を実行中...")
        usecase = MergeCsvFilesUseCase()
        result = usecase.execute(csv_files, output_dir)
        
        # 結果を表示
        logger.info("-" * 60)
        if result.is_successful:
            logger.info("[成功] 結合処理が成功しました！")
            logger.info(f"   出力ファイル: {result.output_path}")
            logger.info(f"   結合ファイル数: {result.merged_file_count}")
            logger.info(f"   総行数: {result.total_rows}")
            logger.info("=" * 60)
            
            # 標準出力にも表示（テストで確認しやすいように）
            print(f"成功: {result.merged_file_count}ファイルを結合しました（{result.total_rows}行）")
            print(f"出力: {result.output_path}")
            
            return 0
        else:
            logger.error("[失敗] 結合処理が失敗しました")
            logger.error(f"   エラー: {result.error_message}")
            logger.info("=" * 60)
            
            # 標準エラー出力にも表示
            print(f"エラー: {result.error_message}", file=sys.stderr)
            
            return 1
            
    except FileNotFoundError as e:
        logger.error(f"[エラー] ファイルが見つかりません: {e}")
        print(f"エラー: {e}", file=sys.stderr)
        return 1
    
    except ValueError as e:
        logger.error(f"[エラー] 入力エラー: {e}")
        print(f"エラー: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        logger.exception(f"[エラー] 予期しないエラーが発生しました: {e}")
        print(f"予期しないエラー: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
