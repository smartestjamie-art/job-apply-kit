# 06 · 更新资料 / Update profile

1. 只改用户提到的字段；不确定的先问。
2. 改完运行：
   ```bash
   python scripts/validate_profile.py
   python scripts/make_cheatsheet.py
   python scripts/validate_search.py     # 有 config/search.yaml 时：检查两边的经验年限、地点有没有对不上
   ```
   改的是经验年限或目标城市：`config/search.yaml` 里的 `candidate.max_experience_years`、`locations.primary` 也要一起改。
3. 换了简历：放进 `cv/` 对应子文件夹，更新 `cv_variants`，文件名保持统一。
4. 在 `data/progress.md` 记一行“资料更新：……”。
