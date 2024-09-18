#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :gas_or_particle.py
# @Time      :2024/09/18 11:12:59
# @Author    :Haofan Wang



def convert_kg_to_mol(emis_df, molar_mass_g_per_mol):
    """
    Convert emissions from kilograms (kg) to moles (mol), with molar mass in g/mol.

    Parameters:
    emis_kg (float or np.ndarray): Emissions in kilograms.
    molar_mass_g_per_mol (float): Molar mass of the substance in g/mol.

    Returns:
    float or np.ndarray: Emissions in moles.
    """
    # Convert molar mass from g/mol to kg/mol by dividing by 1000
    molar_mass_kg_per_mol = molar_mass_g_per_mol * 1E-3
    
    # Perform the conversion
    emis_df['emissions'] = emis_df['emissions'] * (1 / molar_mass_kg_per_mol)
    return emis_df
