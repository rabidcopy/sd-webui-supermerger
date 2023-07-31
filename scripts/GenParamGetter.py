import gradio as gr
from modules import scripts, script_callbacks

class GenParamGetter(scripts.Script):
    txt2img_gen_button = None
    img2img_gen_button = None

    txt2img_params = []
    img2img_params = []

    def __init__(self) -> None:
        super().__init__()
        script_callbacks.on_app_started(lambda demo, app: self.get_params_components(demo))

    def title(self):
        return "Super Marger Generation Parameter Getter"
    
    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def after_component(self, component: gr.components.Component, **_kwargs):
        """Find generate button"""
        if component.elem_id == "txt2img_generate":
            GenParamGetter.txt2img_gen_button = component
        elif  component.elem_id == "img2img_generate":
            GenParamGetter.img2img_gen_button = component

    def get_components_by_ids(self, root: gr.Blocks, ids: list[int]):
        components: list[gr.Blocks] = []

        if root._id in ids:
            components.append(root)
            ids = [_id for _id in ids if _id != root._id]

        if isinstance(root, gr.components.BlockContext):
            for block in root.children:
                components.extend(self.get_components_by_ids(block, ids))

        return components
    
    def compare_components_with_ids(self, components: list[gr.Blocks], ids: list[int]):
        return len(components) == len(ids) and all(component._id == _id for component, _id in zip(components, ids))

    def get_params_components(self, demo: gr.Blocks):
        dependencies: list[dict] = [x for x in demo.dependencies if x["trigger"] == "click" and (GenParamGetter.txt2img_gen_button._id if self.is_txt2img else GenParamGetter.img2img_gen_button._id) in x["targets"]]
        dependency: dict = None
        cnet_dependency: dict = None
        UiControlNetUnit = None
        for d in dependencies:
            if len(d["outputs"]) == 1:
                outputs = outputs = self.get_components_by_ids(demo, d["outputs"])
                output = outputs[0]
                if (
                    isinstance(output, gr.State)
                    and type(output.value).__name__ == "UiControlNetUnit"
                ):
                    cnet_dependency = d
                    UiControlNetUnit = type(output.value)

            elif len(d["outputs"]) == 4:
                dependency = d

        params = [params for params in demo.fns if self.compare_components_with_ids(params.inputs, dependency["inputs"])]

        if self.is_txt2img:
            GenParamGetter.txt2img_params = params[0].inputs
        elif self.is_img2img:
            GenParamGetter.txt2img_params = params[0].inputs