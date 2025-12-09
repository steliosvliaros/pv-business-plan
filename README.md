\# PV Business Plan - Solar Project Financial Analysis



A comprehensive Python-based tool for analyzing and modeling solar photovoltaic (PV) projects. This repository provides financial modeling, technical analysis, and automated report generation for solar business plans.



!\[CI Status](https://github.com/yourusername/pv-business-plan/workflows/CI%20-%20PV%20Business%20Plan/badge.svg)

!\[Python Version](https://img.shields.io/badge/python-3.12-blue.svg)

!\[License](https://img.shields.io/badge/license-MIT-green.svg)



\## Features



\- 📊 \*\*Financial Modeling\*\*: NPV, IRR, payback period, LCOE calculations

\- ☀️ \*\*Solar Analysis\*\*: Production estimates using pvlib

\- 📈 \*\*Sensitivity Analysis\*\*: Multi-parameter scenario modeling

\- 📄 \*\*Report Generation\*\*: Automated PDF and Excel reports

\- 🗄️ \*\*Database Integration\*\*: PostgreSQL with Alembic migrations

\- 🧪 \*\*Testing Suite\*\*: Comprehensive pytest coverage

\- 🔄 \*\*CI/CD\*\*: GitHub Actions automated testing



\## Quick Start



\### Prerequisites



\- Windows 10/11

\- \[Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed

\- \[PostgreSQL 16+](https://www.postgresql.org/download/windows/) installed

\- Git



\### Installation



1\. \*\*Clone the repository\*\*

```bash

&nbsp;  git clone https://github.com/yourusername/pv-business-plan.git

&nbsp;  cd pv-business-plan

```



2\. \*\*Create conda environment\*\*

```bash

&nbsp;  conda env create -f environment.yml

&nbsp;  conda activate pv\_business\_plan

```



3\. \*\*Configure environment variables\*\*

```bash

&nbsp;  copy .env.example .env

&nbsp;  # Edit .env with your database credentials

```



4\. \*\*Setup database\*\*

```bash

&nbsp;  # Create database

&nbsp;  psql -U postgres

&nbsp;  CREATE DATABASE pv\_business\_db;

&nbsp;  CREATE USER pv\_user WITH ENCRYPTED PASSWORD 'your\_password';

&nbsp;  GRANT ALL PRIVILEGES ON DATABASE pv\_business\_db TO pv\_user;

&nbsp;  \\q

&nbsp;

&nbsp;  # Load schema

&nbsp;  psql -U pv\_user -d pv\_business\_db -f sql/schema.sql

&nbsp;

&nbsp;  # Run migrations

&nbsp;  alembic upgrade head

```



5\. \*\*Install Jupyter kernel\*\*

```bash

&nbsp;  python -m ipykernel install --user --name pv\_business\_plan --display-name "Python 3.12 (PV Business Plan)"

```



6\. \*\*Start Jupyter\*\*

```bash

&nbsp;  jupyter notebook

```



\## Project Structure

```

pv-business-plan/

├── notebooks/          # Jupyter notebooks for analysis

├── src/               # Python source modules

│   ├── db.py          # Database utilities

│   ├── solar\_calculations.py  # PV system modeling

│   ├── financial\_models.py    # Financial analysis

│   └── report\_generation.py   # Report creation

├── tests/             # Test suite

├── sql/               # Database schemas and migrations

├── data/              # Data files (gitignored)

├── reports/           # Generated reports (gitignored)

└── docs/              # Documentation

```



\## Usage Examples



\### Financial Analysis

```python

from src.financial\_models import FinancialInputs, run\_financial\_model



inputs = FinancialInputs(

&nbsp;   system\_capacity\_kw=100.0,

&nbsp;   total\_capex=150000,

&nbsp;   annual\_production\_kwh=140000,

&nbsp;   electricity\_rate\_kwh=0.12,

&nbsp;   opex\_annual=2000,

&nbsp;   escalation\_rate=0.025,

&nbsp;   discount\_rate=0.06,

&nbsp;   project\_lifetime\_years=25

)



results = run\_financial\_model(inputs)

print(f"NPV: ${results\['npv']:,.2f}")

print(f"IRR: {results\['irr']:.2f}%")

```



\### Solar Production Estimate

```python

from src.solar\_calculations import estimate\_annual\_production



production = estimate\_annual\_production(

&nbsp;   system\_capacity\_kw=100.0,

&nbsp;   latitude=33.4484,

&nbsp;   longitude=-112.0740,

&nbsp;   tilt=25.0,

&nbsp;   azimuth=180.0

)



print(f"Annual Production: {production\['annual\_production\_kwh']:,.0f} kWh")

```



\## Development



\### Running Tests

```bash

\# Run all tests

pytest -v



\# Run with coverage

pytest --cov=src --cov-report=html



\# Run specific test file

pytest tests/test\_financial\_models.py -v

```



\### Code Quality

```bash

\# Format code

black src tests



\# Lint

flake8 src tests



\# Type check

mypy src

```



\### Database Migrations

```bash

\# Create new migration

alembic revision -m "description"



\# Apply migrations

alembic upgrade head



\# Rollback one version

alembic downgrade -1

```



\## Contributing



1\. Fork the repository

2\. Create a feature branch (`git checkout -b feature/amazing-feature`)

3\. Make your changes

4\. Run tests and code quality checks

5\. Commit your changes (`git commit -m 'feat: add amazing feature'`)

6\. Push to the branch (`git push origin feature/amazing-feature`)

7\. Open a Pull Request



\## License



This project is licensed under the MIT License - see the \[LICENSE](LICENSE) file for details.



\## Acknowledgments



\- \[pvlib](https://pvlib-python.readthedocs.io/) for solar modeling

\- \[SQLAlchemy](https://www.sqlalchemy.org/) for database ORM

\- \[Alembic](https://alembic.sqlalchemy.org/) for database migrations



\## Support



For questions or issues, please \[open an issue](https://github.com/yourusername/pv-business-plan/issues) on GitHub.
