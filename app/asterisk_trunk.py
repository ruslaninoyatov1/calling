import os
import subprocess
import logging
from typing import Optional
from app.config import Config
from app.models import Company

logger = logging.getLogger(__name__)


def get_trunk_name_for_company(company: Company) -> str:
    """Return a deterministic SIP trunk name for a company."""
    return f"acc_{company.id}"


def _build_chan_sip_peer_config(company: Company, trunk_name: str) -> str:
    """Build chan_sip peer configuration block for a company's SIP account."""
    lines = [
        f"[{trunk_name}]",
        "type=peer",
        f"host={company.link}",
        f"username={company.login}",
        f"fromuser={company.login}",
        f"secret={company.password}",
        "context=outgoing",
        "insecure=invite,port",
        "dtmfmode=rfc2833",
        "qualify=yes",
        "nat=no",
        "canreinvite=no",
        "disallow=all",
        "allow=alaw",
        "trustrpid=yes",
        "sendrpid=pai",
    ]
    return "\n".join(lines) + "\n"


def ensure_trunk_for_company(company: Company) -> Optional[str]:
    """
    Create or update a chan_sip trunk config snippet for the given company and reload Asterisk.
    Returns the trunk name if successful; None if failed.
    """
    try:
        trunk_name = get_trunk_name_for_company(company)
        os.makedirs(Config.SIP_AUTOCALLER_DIR, exist_ok=True)
        conf_path = os.path.join(Config.SIP_AUTOCALLER_DIR, f"{trunk_name}.conf")
        content = _build_chan_sip_peer_config(company, trunk_name)
        with open(conf_path, "w") as f:
            f.write(content)

        # Set safe permissions if possible
        try:
            os.chmod(conf_path, 0o644)
        except Exception:
            pass

        # Try reloading chan_sip
        reload_cmd = ["asterisk", "-rx", "sip reload"]
        try:
            proc = subprocess.run(reload_cmd, check=True, capture_output=True, text=True)
            logger.info(f"Asterisk SIP reloaded for trunk {trunk_name}: {proc.stdout.strip()}")
        except Exception as e:
            logger.warning(f"Could not reload Asterisk SIP: {e}")

        return trunk_name
    except Exception as e:
        logger.error(f"Failed to ensure trunk for company {company.id}: {e}")
        return None