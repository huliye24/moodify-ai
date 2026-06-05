You are processing one Moodify optimization micro-task.

Return JSON only.
Do not write markdown.
Do not inspect code.
Do not invent missing fields.
Use only the input record.

Allowed loop values:
- runtime_reliability
- scoring_calibration
- craft_preset_selection
- operator_report

Allowed severity values:
- low
- medium
- high

Output schema:
{
  "task_id": "copy from input",
  "loop": "copy from input",
  "severity": "low|medium|high",
  "reason": "short reason under 180 chars",
  "next_action": "one concrete action under 220 chars",
  "needs_human_review": true
}
