# AI-Image Project Memory

## Project Structure (V6.8 — Post-refactor)

### Root (20 entry scripts)
- `generate.py`, `img2img.py`, `inpaint.py`, `recompose.py` — core generation
- `cast.py`, `batch_cast.py`, `video_cast.py` — character casting (image + video)
- `generate_with_lora.py`, `batch_generate_lora.py`, `batch_generate_features.py`, `batch_scenes.py` — batch generation
- `create_scene.py` — scene preset creation (single image + batch folder mode)
- `style.py` — standalone style entry (no importers, has `__main__`)
- `interrogate_image.py`, `reverse_feature.py`, `create_feature.py` — utilities
- `install.py`, `civitai.py` — model management
- `curate_dataset.py`, `train_character.py` — training pipeline

### core/ (12 modules + 2 subpackages)
```
core/
├── model_registry.py       # 底模配置注册表 (Janku primary / Pony V6 secondary)
├── comfy_utils.py          # ComfyUI auto-start + task polling (canonical)
├── video_utils.py          # FFmpeg integration + keyframe management (V2V)
├── llm_client.py           # Unified LLM interface (Ollama/DeepSeek)
├── lora_config.py          # LoRA config + LLMResponse
├── lora_stack.py           # Multi-LoRA stacking
├── prompt_merger.py        # PNG metadata extraction + merge
├── scene_loader.py         # Feature config + discover_features() + load_scene_preset/list_scene_presets
├── tag_cleaner.py          # WD14 tag cleaning + style injection (STYLE_REGISTRY)
├── workflow_nodes.py       # Workflow node ID management
├── workflow_selector.py    # Workflow selection logic
├── extractors/             # 4 modules: base, png_metadata, prompt, vision
└── prompts/                # 7 modules: character, character_lora, flux, img2img, inpaint, interrogate, pony
```

### Key directories
- **features/**: 5 scene dirs (beach, gym, hotspring, intimate, leotard) with symlinks → `scripts/feature_cast.py` & `scripts/feature_generate.py`
- **workflows/**: flux/, img2img/, inpaint/, interrogate/, recompose/, sdxl/ (active + archived/)
- **scenes/**: 88 scene pose preset YAMLs (.gitignore), used by `--scene` mode
- **docs/**: features/ (7), decisions/ (6 ADR), styles/ (3), archived/
- **lora_presets/**: LoRA stack YAML configs (tracked in git)

## V6.8 Refactoring Summary (2026-02-24~25)

### Completed refactors (committed)
1. **`generate_with_lora.py`**: 1355 → 935 lines (-31%), `main()` 589 → 105 lines
   - Introduced `ResolvedConfig` dataclass replacing ~15 scattered variables
   - Extracted 8 helper functions: `_build_scene_preset_prompt`, `_build_feature_prompt`, `_apply_scene_adjustments`, `_apply_custom_style_lora`, `_apply_feature_loras`, `_resolve_model_params`, `_submit_and_save`, `_handle_list_commands`
   - `build_workflow()` takes 1 `ResolvedConfig` instead of 18 params
   - System prompts → `core/prompts/character_lora.py`
   - `load_scene_preset`/`list_scene_presets` → `core/scene_loader.py` (also updated `cast.py`)
   - Added `SKIN_TEXTURE_BOOST` global effect (default on, `--no-skin-boost` to disable)

2. **`reverse_feature.py`**: 989 → 721 lines, eliminated duplicate patterns

3. **`llm_client.py` (core)**: 1088 → 815 lines, eliminated duplicate patterns

4. **Scene mode decoupling**: `cast.py` supports `--scene / --list-scenes`, scene YAML controls composition

5. **`create_scene.py`**: Added batch folder mode (auto-numbered from `--start`), code-side identity filtering

6. **`batch_scenes.py`**: Added `--style` parameter, pre-translation to avoid N×LLM calls

### Pending in working tree (uncommitted)
- `curate_dataset.py`: Pose diversity protection tags added, section header cleanup (+454/-150 net)
- `train_character.py`: Added `--retrain` flag, smart skip when output exists (+33 lines)
- `batch_scenes.py`: `--style` parameter passthrough (+13 lines)
- `create_scene.py`: Batch folder mode enhancement (+232 lines net)
- **Note**: `core/aesthetic_scorer.py` and `core/report_generator.py` NOT yet extracted (planned but not done)

### V6.8 task file status
- Stage 0 "低风险清理" (parallel): completed (V6.6 era — extractors restore, discover_features dedup, polling dedup, dead code)
- Stage 1 "集成验证": completed
- Stage 2 "文档同步": in progress (current task)
- Stage "大文件拆分" (curate_dataset, feature_generate): **NOT started** — was planned but deferred

## Canonical Locations (post-refactor)

| Function | Canonical Location |
|----------|-------------------|
| `discover_features()` | `core/scene_loader.py` |
| `load_scene_preset()` / `list_scene_presets()` | `core/scene_loader.py` |
| `list_characters()` | Still duplicated in generate_with_lora, batch_generate_lora, batch_scenes (NOT yet consolidated) |
| `discover_scene_presets()` | `batch_scenes.py` (own implementation, NOT same as `list_scene_presets()`) |
| `CHARACTER_LORA_SYSTEM_PROMPT` / `FEATURE_FUSION_SYSTEM_PROMPT` | `core/prompts/character_lora.py` |
| ComfyUI polling/ensure | `core/comfy_utils.py` |
| WD14/CLIP extractors | `core/extractors/prompt.py` |
| Vision (Florence-2) | `core/extractors/vision.py` |
| PNG metadata extraction | `core/extractors/png_metadata.py` |
| Model config (checkpoint, sampler, quality prefix) | `core/model_registry.py` |
| Style negative (model-independent) | `core/tag_cleaner.py` STYLE_REGISTRY |

## Key Lessons

### Import Migration
- `sed -i` on symlinks converts them to real files — must restore symlinks after
- `workflow_selector.py` auto-matches scene names to workflow JSON files — check before archiving
- `features/*/cast.py` and `generate.py` are symlinks to `scripts/feature_cast.py` and `scripts/feature_generate.py`
- Many scripts use **delayed imports** (inside functions) — regex must handle indented imports too

### Verification Before Archiving
- Always check `features/*/config.yaml` for workflow references (hires_fix.workflow field)
- Some workflows are implicitly referenced by scene name matching
- Pattern: `scene_name.replace("-", "_") + ".json"`

### Dead Code Indicators
- Duplicate utility functions accumulate across files — consolidate on detection
- `style.py` has `__main__` but 0 importers — it's an entry script, not a library

### Remaining Duplication (V6.8 backlog)
- `list_characters()` still in 3 files (generate_with_lora, batch_generate_lora, batch_scenes)
- `list_features()` still in batch_cast + batch_generate_features (different display logic)
- `curate_dataset.py` still monolithic (1965 lines) — aesthetic_scorer + report_generator not extracted
- `scripts/feature_generate.py` still has 533-line `generate_image()` function

### Gate Verification Command
```bash
source venv/bin/activate && python -c "from core.extractors.prompt import WD14Extractor; from core.scene_loader import discover_features, load_scene_preset; import interrogate_image; import generate_with_lora; import cast; print('Gate PASSED')"
```

## V6.7 Janku Model Switch (2026-02-23)

### Key model differences
| Param | Janku (Illustrious XL) | Pony V6 XL |
|-------|----------------------|------------|
| CFG | 5.0 | 7.0 |
| Steps | 30 | 40 |
| Sampler | euler | euler_ancestral |
| Resolution | 1024x1536 | 832x1216 |
| Quality prefix | masterpiece, best quality | score_9, score_8_up |
| Tag system | danbooru (native) | pony_score |

### CLI: `--model janku` (default) / `--model pony_v6` / `--basemodel xxx.safetensors`

## Video-to-Video Feature — SHELVED (2026-03-02)

**Status**: Terminated. Code deleted, ADR at `docs/decisions/007-v2v-shelved.md`.

**Root cause**: Img2Img denoise is a global knob — high denoise changes character but destroys composition, low denoise preserves composition but character unchanged. Masked inpaint (SetLatentNoiseMask) partially works (background preserved, pose aligned) but LoRA features still can't fully override at safe denoise levels.

**Conclusion**:逐帧 Img2Img + ControlNet 不是 V2V 角色替换的正确工具。未来应直接上端到端视频模型 (Wan2.1, AnimateDiff-Evolved, 商业 SaaS)。

**Installed models still present** (可复用):
- `illustriousXL_v10.safetensors` — OpenPose ControlNet
- `comfyui_controlnet_aux` — DWPose/OpenPose preprocessor node

## Recent Features (2026-02-24~25)

- **SKIN_TEXTURE_BOOST**: `(shiny skin:1.2), (wet skin:1.1), (oil:1.1)` — global in `generate_with_lora.py`, default on, `--no-skin-boost` to disable
- **Scene preset creation**: `create_scene.py` supports single image (`--name` required) and batch folder mode (`--start` for numbering)
- **88 scene presets** in `scenes/` directory (up from ~55 hand-written)

## Major Cleanup (2026-03-02) — ~133G freed

### Round 1: Feature cleanup
- Reduced features 23 → 5 (beach, gym, hotspring, intimate, leotard)
- Deleted 17 feature dirs + 12 LoRAs (~3.7G)

### Round 2: Cache + duplicates
- pip cache (~21G), HF FLUX.1-dev cache (~32G), ai-toolkit duplicate checkpoints (~26G)

### Round 3: Unused models
- 5 checkpoints: prefectIllustriousXL_v60, bismuthIllustrious_v60, waiIllustriousSDXL_v110, hassakuv13StyleA, SDXL_base (~32.5G)
- 22 LoRAs: MGE_V7.0, 748cmSDXL, Hand pony, chefhatchetpxl, 69yottea_illu_v2, Niji_mix, g0th1c2XLP, Gothic_Realistic, MythPortrait, Horseman, add-detail-xl, USNR_XL_lokr, USNR_NB_V3, zimage, kafu, atalanta, Abstract Painting, Bill_Cipher, milktea_sdxl, test_char_lora, kisume, black_lora (~5G)
- 2 obsolete workflows: bedfeet.json, bedroom.json
- black_card.yaml character card
- ai-toolkit test outputs: test_char, test_char_v2 (~1.6G)

### Remaining models: see `docs/MODEL_INVENTORY.md`
- 7 checkpoints (46G), 28 LoRAs (9G), all with code references
- 8 Flux LoRAs in code but NOT installed (placeholder presets, no disk cost)
- Flux training models (~118G in ~/flux-training/) still present but unused

## Face LoRA 分离方案 (2026-03-13)
- [project_face_lora_plan.md](project_face_lora_plan.md) — Gemini 咨询结论: 方案 D (Prompt 身体 + Face LoRA)，资产命名约定，实现路径

## Ollama Docker 配置 (2026-03-13)
- [project_ollama_docker.md](project_ollama_docker.md) — Docker volume 选择、dolphin-nemo 模型、WSL2 bind mount 陷阱

## 项目拆分 (2026-03-20)
- [project_split_2026_03_20.md](project_split_2026_03_20.md) — ai-image 重命名为 local-images, 新建 ai-images (SFW SDXL)
