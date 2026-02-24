import os
from website import WebsiteGraph
from playwright import Playwright
from pydantic_ai import Agent, RunContext
from cache import cache
from util import Util

agent = Agent(
    model=os.getenv("LLM_MODEL"),
    deps_type=dict,
    output_type=str,
    system_prompt="你是一个网站图谱管理助手，你可以帮助用户管理和更新网站图谱。用户会通过一系列工具与你交互来完成任务。"
)


@agent.tool
def get_website_graph(ctx: RunContext[dict]) -> str:
    """获取网站图谱和页面内容相似度矩阵"""
    graph: WebsiteGraph = ctx.deps["graph"]
    return graph.to_readable()


@agent.tool
def website_graph_add_node(ctx: RunContext[dict], url: str, title: str, snapshot_hex: str) -> int:
    graph: WebsiteGraph = ctx.deps["graph"]
    node_id = graph.add_node(
        url=url,
        title=title,
        snapshot=cache.get(snapshot_hex)
    )
    return node_id


@agent.tool
def website_graph_delete_node(ctx: RunContext[dict], node_id: int) -> None:
    graph: WebsiteGraph = ctx.deps["graph"]
    graph.delete_node(node_id)


@agent.tool
def website_graph_update_node_desc(ctx: RunContext[dict], node_id: int, desc: str) -> None:
    """更新页面整体描述"""
    graph: WebsiteGraph = ctx.deps["graph"]
    graph.update_node(node_id, "desc", desc)


@agent.tool
def website_graph_update_node_features(ctx: RunContext[dict], node_id: int, features: list[str]) -> None:
    """更新页面功能描述"""
    graph: WebsiteGraph = ctx.deps["graph"]
    graph.update_node(node_id, "features", features)


@agent.tool
def website_graph_update_node_datas(ctx: RunContext[dict], node_id: int, datas: list[str]) -> None:
    """更新页面数据描述"""
    graph: WebsiteGraph = ctx.deps["graph"]
    graph.update_node(node_id, "datas", datas)


@agent.tool
def website_graph_update_summary(ctx: RunContext[dict], summary: str) -> None:
    """更新网站整体描述"""
    graph: WebsiteGraph = ctx.deps["graph"]
    graph.update_summary(summary)


@agent.tool
def website_graph_update_edge(ctx: RunContext[dict], from_node_id: int, to_node_id: int, operation: str) -> None:
    """添加或者修改页面跳转关系, operation表示如何从前一个页面到后一个页面的, 进行了什么操作"""
    graph: WebsiteGraph = ctx.deps["graph"]
    graph.update_edge(from_node_id, to_node_id, operation)


@agent.tool
def browser_open(ctx: RunContext[dict], url: str) -> str:
    """使用浏览器打开指定URL并返回页面内容的文本快照"""
    graph: WebsiteGraph = ctx.deps["graph"]
    pw: Playwright = ctx.deps["pw"]
    text = pw.run("open", url)
    text = text[pos:] if (pos := text.find('### Page')) != -1 else text
    snapshot = pw.run("snapshot")
    print(snapshot)
    ctx.deps["latest_snapshot"] = snapshot
    snapshot_hex = Util.get_text_hex_prefix(snapshot)
    cache.set(snapshot_hex, snapshot)
    result = f"### Snapshot Similarity\n{graph.query_similarity_to_table(snapshot)}\n### Snapshot Hex\n{snapshot_hex}\n" + text
    return result

@agent.tool
def browser_type(ctx: RunContext[dict], text:str) -> None:
    """type text into editable element"""
    graph: WebsiteGraph = ctx.deps["graph"]
    pw: Playwright = ctx.deps["pw"]
    snapshot = pw.run("snapshot")
    return snapshot
