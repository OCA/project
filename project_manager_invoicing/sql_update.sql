# Correction invoiced hours vides
update account_analytic_line set invoiced_hours = unit_amount;
# Correction invoiced product (après installation le met à admin)
update account_analytic_line set invoiced_product_id = product_id;

# Gérer le status "draft" sur les heures déjà envoyées
# par défaut, elles sont toutes settées à 'draft' => celles qui
# sont comptabilisées doivent être mise à 'confirm'