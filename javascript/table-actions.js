

function newElement(element, id, classList = [], label, nodeToAppend) {
  const el = document.createElement(element);
  el.id = id;
  el.classList.add(...classList);
  el.innerHTML = label;
  return nodeToAppend.appendChild(el);
}

class TableActions {
  constructor(element, options) {
    this.table =
      typeof element === "string" ? document.getElementById(element) : element;

    this.tableRows = [
      ...this.table.querySelector("tbody").querySelectorAll("tr"),
    ];

    this.currentPage = 0;

    this.options = {
      sortable: options.sortable ?? false,
      paginable: options.paginable ?? true,
      rowsPerPage: options.rowsPerPage ?? 10,
      checkableRows: options.checkableRows ?? false,
      checkableRowTdReference: options.checkableRowTdReference ?? "[data-ref]",
      checkedElementsCallBack:
        options.checkedElementsCallBack ??
        function (checkedElements) {
          console.log(checkedElements);
        },
    };

    this._init();
  }

  _init() {
    const checkableRows = this.options.checkableRows;
    if (checkableRows) this._setTableCheckBoxes();
    if (this.options.sortable) this._setTableSort(checkableRows);

    if (this.options.paginable) {
      this._setPaginationButtons();
      this._updateTable();
    }
  }

  _setPaginationButtons() {
    const self = this;
    const backButton = newElement(
      "button",
      "back-page",
      ["btn", "btn-pagination"],
      "<",
      self.table.parentNode
    );
    const forwardButton = newElement(
      "button",
      "forward-page",
      ["btn", "btn-pagination"],
      ">",
      self.table.parentNode
    );

    // Click button show all element selected
    backButton.addEventListener("click", function (event) {
      if (self.currentPage > 0) {
        self.currentPage = self.currentPage -= 1;
        self._updateTable();
      }
    });

    forwardButton.addEventListener("click", function (event) {
      if (self.currentPage < self._getLastPage()) {
        self.currentPage = self.currentPage += 1;
        self._updateTable();
      }
    });
  }

  _setTableSort(checkableRows) {
    const self = this;

    // Setting class to activate table arrows styles
    this.table.classList.add("sortable");

    const tableHeads = this.table.querySelectorAll("th");
    for (
      let thIndex = checkableRows ? 1 : 0; // if checkable column jump first
      thIndex < tableHeads.length;
      thIndex++
    ) {
      const th = tableHeads[thIndex];
      const otherTh = [];

      // Getting other columns to remove active icons class colors
      for (const [index, el] of tableHeads.entries()) {
        if (index !== thIndex) otherTh.push(el);
      }

      // Setting events listeners to get click in table headers.
      // Clicks will activate sort to the clicked column
      th.addEventListener("click", function () {
        self._sortTable(th, thIndex, otherTh);
      });
    }
  }

  _sortDataFormat(format, val, nextVal) {
    switch (format) {
      case "DD/MM/YYYY":
        val = val.split("/");
        val = new Date(val[2] + "-" + val[1] + "-" + val[0]);
        nextVal = nextVal.split("/");
        nextVal = new Date(nextVal[2] + "-" + nextVal[1] + "-" + nextVal[0]);
        break;

      case "YYYY/MM/DD":
        val = new Date(val.replace("/", "-"));
        nextVal = new Date(nextVal.replace("/", "-"));

      case "YYYY-MM-DD":
        val = new Date(val);
        nextVal = new Date(nextVal);
        break;

      case "YYYY-MM-DD HH:MM:SS":
        const [valDate, valHour] = val.split(" ");
        val = new Date(valDate + "T" + valHour);
        const [nextValDate, nextValHour] = val.split(" ");
        val = new Date(nextValDate + "T" + nextValHour);
        break;

      default:
        throw new Error(`Format ${format} not recognized`);
        break;
    }

    return [val, nextVal];
  }

  _sortTable(th, thIndex, otherThs) {
    const self = this;
    const asc = th.dataset.asc ? !JSON.parse(th.dataset.asc) : true;
    const format = th.dataset.format;

    for (const otherTh of otherThs) {
      otherTh.removeAttribute("data-asc");
    }

    self.tableRows.sort(function (val, nextVal) {
      val = val.querySelectorAll("td")[thIndex].innerHTML;
      nextVal = nextVal.querySelectorAll("td")[thIndex].innerHTML;
      try{
      if (format) {
        [val, nextVal] = self._sortDataFormat(format, val, nextVal);
      } else {
        const regex = /[\ \,\;\n]/g;

        val = val.replace(regex, "").toLowerCase();
        nextVal = nextVal.replace(regex, "").toLowerCase();

        if (!isNaN(val)) {
          val = parseFloat(val);
          nextVal = parseFloat(nextVal);
        } else {
          val = toNormalForm(val);
          nextVal = toNormalForm(nextVal);
        }
      }
    }
    catch(err) {
      console.log('非数字不能排序');
    }

      if ((asc && val > nextVal) || (!asc && val < nextVal)) {
        return 1;
      }
      if ((asc && val < nextVal) || (!asc && val > nextVal)) {
        return -1;
      }

      // value must be equal to nextValue
      return 0;
    });

    // Adding sorted elements to the table body
    self._updateTable();

    // Updating dataset asc value
    th.dataset.asc = asc;
  }

  _setTableCheckBoxes() {
    // Get class reference to actual table
    const self = this;

    function tableCheckboxInsert(elementType, classes = []) {
      const element = document.createElement(elementType);
      const input = document.createElement("input");

      if (classes.length) {
        element.classList.add(...classes);
      }

      input.type = "checkbox";
      element.appendChild(input);

      return element;
    }

    // Add table header checkbox
    const tr = self.table.querySelector("thead>tr");
    tr.prepend(tableCheckboxInsert("th", ["tb-checkbox-column"]));

    // Add table rows checkbox
    for (const tr of self.table.querySelectorAll("tbody>tr")) {
      tr.prepend(tableCheckboxInsert("td", ["tb-checkbox-row"]));
    }

    // Set interaction button
    const button = newElement(
      "button",
      "interact",
      ["btn"],
      "Interact",
      self.table.parentNode
    );

    // Click button show all element selected
    button.addEventListener("click", function (event) {
      const checked = [];
      for (const row of self.tableRows) {
        if (row.querySelector("[type='checkbox']").checked) {
          checked.push(
            row.querySelector(self.options.checkableRowTdReference).dataset.ref
          );
        }
      }

      self.options.checkedElementsCallBack(checked);
    });

    // Table checkboxes logic, check all and check one by one
    var checkboxes = document.querySelectorAll("[type='checkbox']");

    for (const checkbox of checkboxes) {
      checkbox.addEventListener("click", function (event) {
        const thead = event.target.closest("thead");

        if (thead) {
          for (const el of self.tableRows) {
            const checkbox = el.querySelector("[type='checkbox']");
            if (event.target.checked) {
              checkbox.checked = true;
              checkbox.closest("tr").classList.add("checked");
            } else {
              checkbox.checked = false;
              checkbox.closest("tr").classList.remove("checked");
            }
          }
        } else {
          self.table.querySelector("thead [type='checkbox']").checked = false;
          event.target.closest("tr").classList.toggle("checked");
        }
      });
    }
  }

  _getCurrentStartRow() {
    return this.options.rowsPerPage * this.currentPage;
  }

  _getLastPageRow() {
    return this._getCurrentStartRow() + this.options.rowsPerPage;
  }

  _getLastPage() {
    return Math.ceil(this.tableRows.length / this.options.rowsPerPage) - 1;
  }

  _updateTable() {
    const self = this;
    const tbody = self.table.querySelector("tbody");

    if (self.options.paginable) {
      tbody.innerHTML = "";
      for (
        let i = self._getCurrentStartRow();
        i < self._getLastPageRow() && i < self.tableRows.length;
        i++
      ) {
        tbody.appendChild(self.tableRows[i]);
      }

      // Update buttons state
      self._updateButtons();
    } else {
      for (const row of self.tableRows) {
        tbody.appendChild(row);
      }
    }
  }

  _updateButtons() {
    const self = this;

    if (self.currentPage === self._getLastPage()) {
      self.table.parentNode.querySelector("#forward-page").disabled = true;
    } else {
      self.table.parentNode.querySelector("#forward-page").disabled = false;
    }

    if (self.currentPage === 0) {
      self.table.parentNode.querySelector("#back-page").disabled = true;
    } else {
      self.table.parentNode.querySelector("#back-page").disabled = false;
    }
  }
}
