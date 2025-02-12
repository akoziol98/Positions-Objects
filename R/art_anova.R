# GITHUB
# Load necessary libraries
library(ARTool)      # For performing ART ANOVA
library(emmeans)     # For post-hoc analysis
library(ggplot2)     # For plotting
library(dplyr)       # For data manipulation
library(car)         # For calculating VIF
library(lme4)
library(onewaytests)
library(moments)
library(tidyverse)
library(nparLD)
library(writexl)

data <- read_csv(DATA)

# Convert independent variables to factors
data$Condition <- factor(data$Condition)
data$Affordances <- factor(data$Affordances)

# Skewness
hist(data$count_per_min)
skewness_value <- skewness(data$count_per_min)
print(skewness_value)

# Statistics
variances <- data %>%
  group_by(Condition, Affordances) %>% # Group by the 2x2 design factors
  summarise(
    Variance = var(count_per_min, na.rm = TRUE), # Calculate variance for each group
    Count = n(),                           # Count of observations per group
    .groups = "drop"                       # Drop group structure after summarization
  )

means <- data %>%
  group_by(Condition, Affordances) %>% # Group by the 2x2 design factors
  summarise(
    mean = mean(count_per_min, na.rm = TRUE), # Calculate variance for each group
    Count = n(),                           # Count of observations per group
    .groups = "drop"                       # Drop group structure after summarization
  )

# Perform Brown-Forsythe test
tests <- list(
  "Other vs sitting (Affordances: graspable)" = bf.test(count_per_min ~ Condition, data = data %>% filter(Affordances == 'graspable')),
  "Other vs sitting (Affordances: stationary)" = bf.test(count_per_min ~ Condition, data = data %>% filter(Affordances == 'stationary')),
  "stationary vs graspable (Condition: Independent sitting)" = bf.test(count_per_min ~ Affordances, data = data %>% filter(Condition == 'Independent sitting')),
  "stationary vs graspable (Condition: Other)" = bf.test(count_per_min ~ Affordances, data = data %>% filter(Condition == 'Other'))
)

# Collect all results into a data frame
bf_results <- do.call(rbind, lapply(names(tests), function(name) {
  test_result <- tests[[name]]
  data.frame(
    Test = name,
    Statistic = test_result$statistic,
    p_value = test_result$p.value,
    df = paste(test_result$parameter, collapse = ", ") 
  )
}))

bf_results <- bf_results%>%
  mutate(across(where(is.numeric), ~ round(., 3)))

# ANOVA
data$Time <- data$count_per_min
hist(data$Time)

# Fit the ART model with log-transformed dependent variable
art_model <- art(Time ~ Condition * Affordances + (1 | id), data = data)

# Perform ANOVA on the ART model and save the summary
anova_results <- anova(art_model)
anova_results$part.eta.sq = with(anova_results, `F` * `Df` / (`F` * `Df` + `Df.res`))
anova_results_summary <- as.data.frame(anova_results)
anova_results_summary <- anova_results_summary %>%
  mutate(across(where(is.numeric), ~ round(., 3)))
anova_results_summary

# Perform post-hoc comparisons using art.con and save the summaries
# Pairwise comparisons for Condition
condition_contrasts <- summary(art.con(art_model, "Condition"))
condition_contrasts_summary <- as.data.frame(condition_contrasts)
condition_contrasts_summary <- condition_contrasts_summary %>%
  mutate(across(where(is.numeric), ~ round(., 3)))

# Pairwise comparisons for Affordances
affordances_contrasts <- summary(art.con(art_model, "Affordances"))
affordances_contrasts_summary <- as.data.frame(affordances_contrasts)
affordances_contrasts_summary <- affordances_contrasts_summary %>%
  mutate(across(where(is.numeric), ~ round(., 3)))

# Pairwise comparisons for Condition:Affordances interaction
interaction_contrasts <- summary(art.con(art_model, "Condition:Affordances"))
interaction_contrasts_summary <- as.data.frame(interaction_contrasts)
interaction_contrasts_summary <- interaction_contrasts_summary %>%
  mutate(across(where(is.numeric), ~ round(., 3)))

# Fit linear models for each term using the aligned rank transformed data
lm_condition <- artlm(art_model, "Condition")
lm_affordances <- artlm(art_model, "Affordances")
lm_interaction <- artlm(art_model, "Condition:Affordances")

# Cohen's d for contrasts
condition_contrasts_summary$d = condition_contrasts_summary$estimate / sigmaHat(lm_condition)
affordances_contrasts_summary$d = affordances_contrasts_summary$estimate / sigmaHat(lm_affordances)
interaction_contrasts_summary$d = interaction_contrasts_summary$estimate / sigmaHat(lm_interaction)

# Check assumptions for the ART model

# 1. Q-Q plot for residuals
# Extract residuals from the linear models used in ART
residuals_art <- resid(lm_interaction)
qq_plot_residuals <- qqnorm(residuals_art)
qqline(residuals_art, col = "red")

# 2. Plot residuals vs fitted values to check for heteroscedasticity
fitted_values_art <- fitted(lm_interaction)
residuals_vs_fitted_plot <- ggplot(data.frame(fitted_values_art, residuals_art), aes(x = fitted_values_art, y = residuals_art)) +
  geom_point() +
  geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
  labs(title = "Residuals vs Fitted Values (ART ANOVA)", x = "Fitted Values", y = "Residuals")

# 3. Q-Q plot for random effects
random_effects_art <- ranef(lm_interaction, condVar = TRUE)
random_effects_df_art <- as.data.frame(random_effects_art$id)
qq_plot_random_effects <- qqnorm(random_effects_df_art$`(Intercept)`)
qqline(random_effects_df_art$`(Intercept)`, col = "red")

# 4. Check linearity by plotting Time against Condition and Affordances
Time_condition_plot <- ggplot(data, aes(x = Condition, y = Time)) +
  geom_boxplot() +
  labs(title = "Time by Condition (ART ANOVA)", x = "Condition", y = "Time")

Time_affordances_plot <- ggplot(data, aes(x = Affordances, y = Time)) +
  geom_boxplot() +
  labs(title = "Time by Affordances (ART ANOVA)", x = "Affordances", y = "Time")

# 5. Check for multicollinearity using VIF
vif_values_art <- vif(lm_interaction)
vif_values_summary <- as.data.frame(vif_values_art)
vif_values_summary <- vif_values_summary %>%
  mutate(across(where(is.numeric), ~ round(., 3)))

# Combine the summaries into a list of data frames
summary_list <- list(
  ANOVA_Results = anova_results_summary,
  Condition_Contrasts = condition_contrasts_summary,
  Affordances_Contrasts = affordances_contrasts_summary,
  Interaction_Contrasts = interaction_contrasts_summary,
  VIF_Values = vif_values_summary,
  variances = variances,
  Means = means,
  BF_test = bf_results
)

# Save the summaries to an Excel file
write_xlsx(summary_list, path = RESULTS)
