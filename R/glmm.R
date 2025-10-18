library(glmmTMB)      
library(emmeans)     
library(dplyr)       
library(car)         
library(moments)
library(tidyverse)
library(partR2)
library(see)

data <- read_csv(DATA)

# Convert independent variables to factors
data$Position <- factor(data$Position)
data$Object <- factor(data$Object)

# Skewness
hist(data$Y_var)
skewness_value <- skewness(data$Y_var)

## ---------------------------------------------------------
## GLMM: Gamma with log link; Conditional and Marginal R2
## ---------------------------------------------------------
glmm_model <- glmmTMB(
  Duration ~ Position * Object + (1 | id),
  family = Gamma(link = "log"),
  data = data
)

Anova_results <- car::Anova(glmm_model, type = "III")
print(Anova_results)
performance::r2_nakagawa(glmm_model)


## ---------------------------------------------------------
## Post-hoc comparisons; Cohen's d
## ---------------------------------------------------------
emm <- emmeans(glmm_model, ~ Position * Object, type = "response")
pairs(emmeans(glmm_model, ~ Position), adjust = "tukey", type = "response")
pairs(emmeans(glmm_model, ~ Object), adjust = "tukey", type = "response")
pairs(emmeans(glmm_model, ~ Position * Object), adjust = "tukey", type = "response")

eff_Position <- emmeans(glmm_model, ~ Position)
eff_Object <- emmeans(glmm_model, ~ Object)
eff_interaction <- emmeans(glmm_model, ~ Position * Object)

eff_size(eff_Position, sigma = sigma(glmm_model), edf = Inf)
eff_size(eff_Object, sigma = sigma(glmm_model), edf = Inf)
eff_size(eff_interaction, sigma = sigma(glmm_model), edf = Inf)

