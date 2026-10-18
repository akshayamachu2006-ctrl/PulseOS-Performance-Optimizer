

def suggest_optimization(label, cpu, memory, disk):
    suggestions = []

    if label == "High Load":
        if cpu > 80:
            suggestions.append(
                "CPU usage is high. Close unused applications."
            )

        if memory > 85:
            suggestions.append(
                "RAM usage is high. Close unused tabs and apps."
            )

        if disk > 80:
            suggestions.append(
                "Disk usage is high. Review files for cleanup."
            )

    elif label == "Medium Load":
        suggestions.append(
            "System is moderately loaded. Monitor performance."
        )

        if disk > 80:
            suggestions.append(
                "Disk usage is high. Consider cleaning temporary files."
            )

    else:
        suggestions.append(
            "System is running normally. No action is needed."
        )

    print(f"\nLoad Status: {label}")

    for suggestion in suggestions:
        print(" ->", suggestion)

    return suggestions

