from website import WebsiteGraph
from playwright import Playwright


if __name__ == "__main__":
    scope = "example.com"

    with Playwright(headed=True) as pw:

        graph = WebsiteGraph(scope)
        print(graph.to_yaml())
        print(graph.similarity_matrix_to_table())

        print(pw.run("open", scope))
    