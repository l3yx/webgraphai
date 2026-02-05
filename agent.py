import os
from website import WebsiteGraph
from playwright import Playwright
from pydantic_ai import Agent, RunContext
from cache import cache

agent = Agent(
    model=os.getenv("LLM_MODEL"),
    deps_type=tuple[WebsiteGraph, Playwright],
    output_type=str,
    system_prompt="你是一个网站图谱管理助手，你可以帮助用户管理和更新网站图谱。用户会通过一系列工具与你交互来完成任务。 你现在有3个snapshot_hex用于测试：7eca689f，098f6bcd， db06c78d"
)


@agent.tool
def get_website_graph(ctx: RunContext[tuple[WebsiteGraph, Playwright]]) -> str:
    """获取网站图谱和页面内容相似度矩阵"""
    graph, pw = ctx.deps
    return graph.to_readable()


@agent.tool
def website_graph_add_node(ctx: RunContext[tuple[WebsiteGraph, Playwright]], url: str, title: str, snapshot_hex: str) -> int:
    graph, pw = ctx.deps
    node_id = graph.add_node(
        url=url,
        title=title,
        snapshot=cache.get(snapshot_hex)
    )
    return node_id


@agent.tool
def website_graph_delete_node(ctx: RunContext[tuple[WebsiteGraph, Playwright]], node_id: int) -> None:
    graph, pw = ctx.deps
    graph.delete_node(node_id)


@agent.tool
def website_graph_update_node_desc(ctx: RunContext[tuple[WebsiteGraph, Playwright]], node_id: int, desc: str) -> None:
    """更新页面整体描述"""
    graph, pw = ctx.deps
    graph.update_node(node_id, "desc", desc)


@agent.tool
def website_graph_update_node_features(ctx: RunContext[tuple[WebsiteGraph, Playwright]], node_id: int, features: list[str]) -> None:
    """更新页面功能描述"""
    graph, pw = ctx.deps
    graph.update_node(node_id, "features", features)


@agent.tool
def website_graph_update_node_datas(ctx: RunContext[tuple[WebsiteGraph, Playwright]], node_id: int, datas: list[str]) -> None:
    """更新页面数据描述"""
    graph, pw = ctx.deps
    graph.update_node(node_id, "datas", datas)


@agent.tool
def website_graph_update_summary(ctx: RunContext[tuple[WebsiteGraph, Playwright]], summary: str) -> None:
    """更新网站整体描述"""
    graph, pw = ctx.deps
    graph.update_summary(summary)


@agent.tool
def website_graph_update_edge(ctx: RunContext[tuple[WebsiteGraph, Playwright]], from_node_id: int, to_node_id: int, operation: str) -> None:
    """添加或者修改页面跳转关系, operation表示操作"""
    graph, pw = ctx.deps
    graph.update_edge(from_node_id, to_node_id, operation)


def browser_open(ctx: RunContext[tuple[WebsiteGraph, Playwright]], url: str) -> str:
    """使用浏览器打开指定URL并返回页面内容的文本快照"""
    graph, pw = ctx.deps
    return pw.run("open", url)