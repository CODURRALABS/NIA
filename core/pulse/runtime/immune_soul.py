import logging
import os
import sys
from typing import Any

logger = logging.getLogger("ImmuneSoul")

class ImmuneSoul:
    """
    NIA Self-Healing System.
    V17 - Monitors for crashes and uses ForgeAgent to fix code.
    Safeguard: NEVER alters core identity or mission goals.
    """
    def __init__(self, forge: Any, symbolic: Any):
        self.forge = forge
        self.symbolic = symbolic
        print("[IMMUNE]: Universal Immune Soul active. Monitoring runtime integrity...")

    async def heal_module(self, module_path: str, error_msg: str):
        """
        Attempts to rewrite a module to fix a detected error.
        Strictly verifies that core identity remains intact.
        """
        logger.warning(f"ImmuneSoul: Detected failure in {module_path}. Error: {error_msg}")
        
        # 1. Read the broken code
        with open(module_path, 'r') as f:
            broken_code = f.read()
            
        # 2. Ask ForgeAgent to generate a fix
        fix_prompt = (
            f"SYSTEM HEALING ERROR: {error_msg}\n"
            f"FILE: {module_path}\n"
            "INSTRUCTION: Fix the error while maintaining the 'Gentleman' persona. "
            "IMPORTANT: DO NOT remove the strings 'FOR_USER', 'BY_USER', or 'AS_USER'."
        )
        
        fixed_code = await self.forge.generate_logic_fix(module_path, broken_code, fix_prompt)
        
        # 3. IDENTITY INTEGRITY CHECK
        if self.symbolic.verify_identity_integrity(fixed_code):
            # SAFE TO APPLY
            with open(module_path, 'w') as f:
                f.write(fixed_code)
            logger.info(f"ImmuneSoul: Successfully repaired {module_path}. Integrity Verified.")
        else:
            logger.error(f"ImmuneSoul: ATTEMPTED CORE VIOLATION BLOCKED. Identity Guard triggered for {module_path}.")
            # Fallback: Restore from internal DNA seed if necessary
