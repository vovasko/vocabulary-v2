import flet as ft

class StatsPieChart(ft.PieChart): 
    # Pie Chart that displays up to 5 values
    def __init__(self, display_data: list[dict], main_color: str = None, caption: ft.Ref[ft.Text] = None):
        super().__init__(sections_space=0, center_space_radius=25, width=150, height=150)
        # Data setup
        self.display_data = sorted(display_data, key=lambda x: x["count"], reverse=True) # Sort data by "count"
        self.total_words = max(sum(item["count"] for item in self.display_data), 1)
        for item in self.display_data:
            item["percentage"] = int(item["count"] / self.total_words * 100)
        
        # Colors setup
        self.main_color = main_color if main_color != None else "INDIGO"
        self.colors = [getattr(ft.Colors, f"{self.main_color}_{shade}") for shade in [500,600,700,800,900]]

        # Styles
        self.normal_style = {
            "radius": 40,
            "title": ft.TextStyle(
                size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD
            )
        }
        self.hover_style = {
            "radius": 50,
            "title": ft.TextStyle(
                size=22, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD,
                shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.BLACK54),
            )
        }

        # Fill with data
        self.caption_text = caption.current
        self.on_chart_event = self.chart_event
        self.fill_sections()

    def chart_event(self, e: ft.PieChartEvent):
        current_stat_text = ""
        for idx, section in enumerate(self.sections):
            if idx == e.section_index:
                section.radius = self.hover_style["radius"]
                section.title_style = self.hover_style["title"]
                # section.title = section.data["stat_name"]
                current_stat_text = f"{section.data["stat_name"]} - {section.data["count_val"]}"
                # section.title_position=0.8
            else:
                section.radius = self.normal_style["radius"]
                section.title_style = self.normal_style["title"]
                # section.title = section.data["count_val"]
                # section.title_position=0.5
        self.caption_text.value = current_stat_text
        self.caption_text.update()
        self.update()

    def fill_sections(self):
        self.sections = [
            ft.PieChartSection(
                # value=min(elem["percentage"], 7),
                value=elem["percentage"],
                # title=elem["name"] if elem["percentage"] > 5 else None,
                title_style=self.normal_style["title"],
                color=self.colors[i],
                radius=self.normal_style["radius"],
                data={"count_val":elem["count"], "stat_name":elem["name"]}
            ) for i, elem in enumerate(self.display_data)
        ]