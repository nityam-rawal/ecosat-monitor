# Alembic initialization script

"""Initial migration."""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Database schema upgrade."""
    # Tables are created via init_db() in app.db.session
    # This file is a placeholder for manual migrations if needed
    pass


def downgrade() -> None:
    """Database schema downgrade."""
    pass
