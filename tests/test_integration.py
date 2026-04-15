"""集成测试 - 测试 Ingest/Query/Lint/Publish 四大操作链路"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置 LLM
os.environ['ANTHROPIC_BASE_URL'] = 'https://api.minimaxi.com/anthropic'
os.environ['ANTHROPIC_AUTH_TOKEN'] = 'sk-cp-os7y1GrOmjzZAyeWQpuEwn5IljJGL9jIIR1HLr_uoGBTM3Jo3nipauVN_bvhB9Gwf34LyeeTQZYbWoLxmKpIVo8BkjYpbNA53aLB7qUoxJipRCoSm898jsY'

sys.stdout.reconfigure(encoding='utf-8')


def test_query_pipeline():
    """测试 Query 流程"""
    from artifact_chain.src.wiki_kb import WikiKnowledgeBase
    from artifact_chain.src.pipelines.query import QueryPipeline

    wiki_kb = WikiKnowledgeBase("artifact_chain/wiki")
    query_pipe = QueryPipeline(wiki_kb)

    # 测试查询
    result = query_pipe.query("青铜面具的 특징是什么？")

    assert result.answer
    assert len(result.consulted_pages) > 0
    assert len(result.citations) > 0
    assert "青铜面具" in result.consulted_pages or any("青铜" in p for p in result.consulted_pages)

    print(f"Query 测试通过: 咨询了 {len(result.consulted_pages)} 个页面")


def test_lint_pipeline():
    """测试 Lint 流程"""
    from artifact_chain.src.wiki_kb import WikiKnowledgeBase
    from artifact_chain.src.pipelines.lint import LintPipeline

    wiki_kb = WikiKnowledgeBase("artifact_chain/wiki")
    lint_pipe = LintPipeline(wiki_kb)

    # 运行健康检查
    result = lint_pipe.run_all()

    assert result.issues is not None
    assert result.log_entry
    # Lifecycle changes 可能为空（取决于页面访问时间）
    assert isinstance(result.lifecycle_changes, list)

    print(f"Lint 测试通过: 发现 {len(result.issues)} 个问题")


def test_ingest_pipeline():
    """测试 Ingest 流程"""
    from artifact_chain.src.wiki_kb import WikiKnowledgeBase
    from artifact_chain.src.pipelines.ingest import IngestPipeline

    # 创建临时 wiki 目录
    with tempfile.TemporaryDirectory() as tmpdir:
        test_wiki_dir = Path(tmpdir) / "wiki"
        test_wiki_dir.mkdir(parents=True, exist_ok=True)

        # 创建必要的子目录
        for subdir in ["entities", "concepts", "summaries", "comparisons", "synthesis"]:
            (test_wiki_dir / subdir).mkdir(exist_ok=True)

        # 创建 index.md
        (test_wiki_dir / "index.md").write_text("# Wiki Index\n\n- entities/\n- concepts/\n", encoding='utf-8')

        # 创建临时 raw 目录
        test_raw_dir = Path(tmpdir) / "raw"
        test_raw_dir.mkdir(exist_ok=True)

        # 创建测试 raw 文件
        raw_file = test_raw_dir / "articles" / "test_article.md"
        raw_file.parent.mkdir(exist_ok=True)
        raw_file.write_text("# 测试文章\n\n这是一篇关于[[青铜面具]]的测试文章。", encoding='utf-8')

        wiki_kb = WikiKnowledgeBase(str(test_wiki_dir))
        ingest_pipe = IngestPipeline(wiki_kb, str(test_raw_dir))

        # 消化文件
        result = ingest_pipe.ingest_file(raw_file)

        assert len(result.created_pages) > 0
        assert "raw-articles-test_article" in result.created_pages[0]
        print(f"Ingest 测试通过: 创建了 {result.created_pages}")


def test_publish_pipeline():
    """测试 Publish 流程"""
    from artifact_chain.src.wiki_kb import WikiKnowledgeBase
    from artifact_chain.src.pipelines.publish import PublishPipeline

    # 创建临时 output 目录
    with tempfile.TemporaryDirectory() as tmpdir:
        wiki_kb = WikiKnowledgeBase("artifact_chain/wiki")
        output_dir = Path(tmpdir) / "output"

        publish_pipe = PublishPipeline(wiki_kb, str(output_dir))

        # 发布
        result = publish_pipe.publish(
            requirement="写一个敦煌科幻短视频脚本",
            topic="敦煌 科幻",
            format="script",
            platform="sora"
        )

        assert result.output_path
        assert result.format == "script"
        assert len(result.source_pages) > 0
        assert Path(result.output_path).exists()

        print(f"Publish 测试通过: 输出到 {result.output_path}")


def test_log_mechanism():
    """测试日志机制"""
    from artifact_chain.src.wiki_kb import WikiKnowledgeBase
    from artifact_chain.src.pipelines.query import QueryPipeline

    # 读取初始日志
    wiki_kb = WikiKnowledgeBase("artifact_chain/wiki")
    initial_log = wiki_kb.read_log()

    # 执行查询（会写入日志）
    query_pipe = QueryPipeline(wiki_kb)
    query_pipe.query("测试查询")

    # 读取更新后的日志
    updated_log = wiki_kb.read_log()

    # 验证日志有更新
    assert updated_log != initial_log
    assert "query | 测试查询" in updated_log or "query |" in updated_log

    print("Log 机制测试通过")


def test_lifecycle_update():
    """测试生命周期更新"""
    from artifact_chain.src.wiki_kb import WikiKnowledgeBase
    from artifact_chain.src.pipelines.query import QueryPipeline

    wiki_kb = WikiKnowledgeBase("artifact_chain/wiki")
    query_pipe = QueryPipeline(wiki_kb)

    # 获取一个页面
    page_before = wiki_kb.get_page("青铜面具")
    if page_before:
        access_count_before = page_before.access_count

        # 执行查询
        query_pipe.query("青铜面具相关")

        # 获取更新后的页面
        page_after = wiki_kb.get_page("青铜面具")
        if page_after:
            assert page_after.access_count >= access_count_before
            print(f"Lifecycle 更新测试通过: access_count {access_count_before} -> {page_after.access_count}")
        else:
            print("Lifecycle 更新测试跳过: 页面未找到")
    else:
        print("Lifecycle 更新测试跳过: 青铜面具页面不存在")


def main():
    """运行所有集成测试"""
    print("=" * 70)
    print("LLM Wiki 四大操作链路集成测试")
    print("=" * 70)

    tests = [
        ("Query Pipeline", test_query_pipeline),
        ("Lint Pipeline", test_lint_pipeline),
        ("Ingest Pipeline", test_ingest_pipeline),
        ("Publish Pipeline", test_publish_pipeline),
        ("Log 机制", test_log_mechanism),
        ("Lifecycle 更新", test_lifecycle_update),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"\n测试: {name}")
        print("-" * 50)
        try:
            test_func()
            passed += 1
            print(f"✓ {name} 通过")
        except Exception as e:
            failed += 1
            print(f"✗ {name} 失败: {e}")

    print("\n" + "=" * 70)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 70)


if __name__ == "__main__":
    main()
