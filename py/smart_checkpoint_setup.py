import comfy.samplers

class SetupSelector:
  def __init__(self):
    pass
  
  @classmethod
  def INPUT_TYPES(cls):
    return {
        "required": {
            "checkpoint_name": ("STRING", {
              "forceInput": True,
              "multiline": False
            }),
            "checkpoint_setups": ("STRING", {
              "forceInput": True,
              "multiline": True
            }),
            "setup_prefix": ("STRING", {
              "default": "!",
              "multiline": False
            }),
            "delmiter": ("STRING", {
              "default": "/",
              "multiline": False
            }),
            "default_setup": ("STRING", {
              "default": "5/20/karras/dpmpp_2m",
              "multiline": False
            })
        }
    }

  RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING","STRING", "LIST")
  RETURN_NAMES = ("set_cfg", "set_steps", "set_scheduler", "set_sampler", "setup_text", "setup")
  
  FUNCTION = "main"
  # OUTPUT_NODE = True
  
  CATEGORY = "Foxpack/Smart Sampler Setup"
  
  def main(self, checkpoint_name, checkpoint_setups, setup_prefix, delmiter, default_setup):
    return_string = ""
    prefixed_name = str(setup_prefix) + str(checkpoint_name)
    
    index = checkpoint_setups.find(prefixed_name)
    
    if index != -1:
        if checkpoint_setups[index + len(prefixed_name)] == '=':
            if checkpoint_setups[index + len(prefixed_name) + 1] == '"':
                start_quote = index + len(prefixed_name) + 2
                end_quote = checkpoint_setups.find('"', start_quote + 1)
                if end_quote != -1:
                    return_string = checkpoint_setups[start_quote:end_quote]
                    print(return_string)
            else:        
                space_index = checkpoint_setups.find(" ", index + len(prefixed_name))
                if space_index != -1:
                    return_string = checkpoint_setups[index + len(prefixed_name):space_index]
                else:
                    return_string = checkpoint_setups[index + len(prefixed_name):]
        else:
            return_string = prefixed_name[1:]

    if return_string == "":
        return_string = default_setup
    
    if return_string.startswith("="):
        return_string = return_string[1:]

    settings = return_string.split(delmiter)

    setup = list(settings)
    setup_text = f"cfg: {settings[0]} | steps: {settings[1]} | scheduler: {settings[2]} | sampler: {settings[3]}"
    return (settings[0], settings[1], settings[2], settings[3], setup_text, setup)
    
  
class BaseSamplerSetup:
  def __init__(self):
    pass
    
  @classmethod
  
  def INPUT_TYPES(s):
    return {
        "required": {
            "setup": ("LIST", {
              "forceInput": True
            }),
            "cfg": ("FLOAT", {
                "default": 1.0,
                "min": 0.0,
                "max": 16.0,
                "step": 0.1,
                "display": "number"
            }),
            "steps": ("INT", {
                "default": 5,
                "min": 1,
                "max": 100,
                "step": 1,
                "display": "number"
            }),
            "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
            "sampler": (comfy.samplers.KSampler.SAMPLERS,),
        }
    }

  RETURN_TYPES = ("FLOAT", "INT", "STRING", "STRING", "STRING", "LIST")
  RETURN_NAMES = ("cfg", "steps", "scheduler", "sampler", "setup_text", "selected_setup")
  FUNCTION = "main"

  def main(self, setup, cfg, steps, scheduler, sampler): 
    def clamp(value, min_value, max_value):
        return max(min_value, min(value, max_value))

    def numeric_range(value):
        if "-" in value:
            parts = value.split("-")
            return (float(parts[0]), float(parts[1]))
        return (float(value), float(value))

    def clamp_in_list(value, lst):
        if value in list(lst):
            return value
        return lst[0]
      
    """main"""
    cfg_range = numeric_range(setup[0])
    clamp_cfg = clamp(cfg, cfg_range[0], cfg_range[1])

    steps_range = numeric_range(setup[1])
    clamp_steps = clamp(steps, steps_range[0], steps_range[1])

    clamp_scheduler = clamp_in_list(scheduler, setup[2].split(","))
    clamp_sampler = clamp_in_list(sampler, setup[3].split(","))

    selected_setup = [clamp_cfg, clamp_steps, clamp_scheduler, clamp_sampler]
    setup_text = f"cfg: {clamp_cfg} | steps: {clamp_steps} | scheduler: {clamp_scheduler} | sampler: {clamp_sampler}"
    
    return (
        float(clamp_cfg),
        int(clamp_steps),
        clamp_scheduler,
        clamp_sampler,
        setup_text,
        selected_setup
    )

  CATEGORY = "Foxpack/Smart Sampler Setup"
    
  
class OverrideSamplerSetup:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "setup": ("LIST", {
                  "forceInput": True
                }),
                "override": (["enabled", "disabled"],{
                  "default": "disabled",
                  "display": "radio"
                }),
                "cfg": ("FLOAT", {
                  "default": 1.0,
                  "min": 0.0,
                  "max": 16.0,
                  "step": 0.1,
                  "display": "number"
                }),
                "steps": ("INT", {
                  "default": 5,
                  "min": 1,
                  "max": 100,
                  "step": 1,
                  "display": "number"
                }),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                "sampler": (comfy.samplers.KSampler.SAMPLERS,),
            },
        }

    RETURN_TYPES = ("FLOAT","INT", comfy.samplers.KSampler.SAMPLERS,
                  comfy.samplers.KSampler.SCHEDULERS, "STRING")
    RETURN_NAMES = ("cfg", "steps", "sampler", "scheduler", "setup_text")
    FUNCTION = "main"

    def main(self, override, setup, steps, cfg, sampler, scheduler):
      cfg_output = cfg if override == "enabled" else setup[0]
      steps_output = steps if override == "enabled" else setup[1]
      scheduler_output = scheduler if override == "enabled" else setup[2]
      sampler_output = sampler if override == "enabled" else setup[3]

      setup_text = f"cfg: {cfg_output} | steps: {steps_output} | scheduler: {scheduler_output} | sampler: {sampler_output}"
      
      return (
        float(cfg_output),
        int(steps_output),
        sampler_output,
        scheduler_output,
        setup_text
      )

    CATEGORY = "Foxpack/Smart Sampler Setup"
