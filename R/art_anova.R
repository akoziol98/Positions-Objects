library(ARTool)      
library(emmeans)     
library(dplyr)       
library(car)         
library(moments)
library(tidyverse)

data <- read_csv(DATA)

# Convert independent variables to factors
data$Position <- factor(data$Position)
data$Object <- factor(data$Object)

# Skewness
hist(data$Y_var)
skewness_value <- skewness(data$Y_var)

# Statistics
variances <- data %>%
  group_by(Position, Object) %>% 
  summarise(
    Variance = var(Y_var, na.rm = TRUE), 
    Count = n(),                           
    .groups = "drop"                       
  )

means <- data %>%
  group_by(Position, Object) %>% 
  summarise(
    mean = mean(Y_var, na.rm = TRUE), 
    Count = n(),                           
    .groups = "drop"                       
  )

# ART-ANOVA

# Fit the ART model 
art_model <- art(Y_var ~ Position * Object + (1 | id), data = data)

# Perform ANOVA on the ART model
anova_results <- anova(art_model)
anova_results$part.eta.sq = with(anova_results, `F` * `Df` / (`F` * `Df` + `Df.res`))
anova_results_summary <- as.data.frame(anova_results)
anova_results_summary <- anova_results_summary %>%
  mutate(across(where(is.numeric), ~ round(., 3)))

# Perform post-hoc comparisons 
# Pairwise comparisons for Position
Position_contrasts <- summary(art.con(art_model, "Position"))
Position_contrasts_summary <- as.data.frame(Position_contrasts)
Position_contrasts_summary <- Position_contrasts_summary %>%
  mutate(across(where(is.numeric), ~ round(., 3)))

# Pairwise comparisons for Object
Object_contrasts <- summary(art.con(art_model, "Object"))
Object_contrasts_summary <- as.data.frame(Object_contrasts)
Object_contrasts_summary <- Object_contrasts_summary %>%
  mutate(across(where(is.numeric), ~ round(., 3)))

# Pairwise comparisons for Position:Object interaction
interaction_contrasts <- summary(art.con(art_model, "Position:Object"))
interaction_contrasts_summary <- as.data.frame(interaction_contrasts)
interaction_contrasts_summary <- interaction_contrasts_summary %>%
  mutate(across(where(is.numeric), ~ round(., 3)))

# Cohen's d for contrasts
Position_contrasts_summary$d = Position_contrasts_summary$estimate / sigmaHat(lm_Position)
Object_contrasts_summary$d = Object_contrasts_summary$estimate / sigmaHat(lm_Object)
interaction_contrasts_summary$d = interaction_contrasts_summary$estimate / sigmaHat(lm_interaction)

